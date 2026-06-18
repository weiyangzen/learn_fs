# Research group subset-b-005642

Work item: `subset-b-005642`

This grouped report covers the eCryptfs files requested for the subset. Each section is source-tree-aligned and wrapped with the exact file markers used by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/crypto.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/crypto.c

## Purpose

`crypto.c` implements eCryptfs' core file-content and filename cryptography. It initializes per-inode `struct ecryptfs_crypt_stat`, encrypts and decrypts page extents, reads and writes the persistent eCryptfs metadata header or `user.ecryptfs` xattr, maps cipher codes to Linux Crypto API names, caches key transform objects, and encodes encrypted filenames into lower-filesystem-safe names. It is the main bridge between VFS-facing code in `file.c`/`inode.c`, key packet handling in `keystore.c`, and lower-file I/O helpers in the rest of the eCryptfs stack.

## Important APIs, types, and functions

The file exports `ecryptfs_init_crypt_stat()`, `ecryptfs_destroy_crypt_stat()`, `ecryptfs_destroy_mount_crypt_stat()`, `ecryptfs_new_file_context()`, `ecryptfs_read_metadata()`, `ecryptfs_write_metadata()`, `ecryptfs_encrypt_page()`, `ecryptfs_decrypt_page()`, `ecryptfs_init_crypt_ctx()`, `ecryptfs_compute_root_iv()`, `ecryptfs_get_tfm_and_mutex_for_cipher_name()`, `ecryptfs_encrypt_and_encode_filename()`, `ecryptfs_decode_and_decrypt_filename()`, and `ecryptfs_set_f_namelen()`. Internal helpers include `crypt_scatterlist()`, `crypt_extent()`, `ecryptfs_read_headers_virt()`, `ecryptfs_write_headers_virt()`, marker/flag conversion helpers, packet length and cipher-code mapping helpers, and filename base64-like encoder/decoder tables.

`struct ecryptfs_flag_map_elem` maps on-disk header flags to in-memory `crypt_stat->flags`. `struct ecryptfs_cipher_code_str_map_elem` maps OpenPGP/RFC2440 cipher codes to Linux cipher names, with special AES key-size handling. Module-global state includes `ecryptfs_key_tfm_cache`, `key_tfm_list`, and `key_tfm_list_mutex`, which cache persistent key encryption TFMs by cipher name.

## Control flow

New encrypted files enter through `ecryptfs_new_file_context()`: mount flags and signatures are copied to the inode, defaults are set, a random FEK is generated, a root IV is computed as MD5(FEK), and a CBC skcipher transform is allocated for the file cipher. `ecryptfs_write_metadata()` allocates a zeroed metadata region, writes the marker, flags, header extent metadata, and key packet set, then persists it either at lower file offset 0 or in `user.ecryptfs` when xattr metadata is enabled.

Existing files enter through `ecryptfs_read_metadata()`: the first lower extent is read, `ecryptfs_read_headers_virt()` validates the marker, initializes upper `i_size`, parses flags/header sizing, then delegates key packet parsing to `ecryptfs_parse_packet_set()`. If the header path fails, the code retries the xattr region and only accepts xattr metadata when the mount enabled xattr support.

Page I/O uses `ecryptfs_encrypt_page()` and `ecryptfs_decrypt_page()`. They translate an upper folio index to a lower byte offset by adding `metadata_size` unless metadata is stored in xattr. Each page is split into `crypt_stat->extent_size` chunks; `crypt_extent()` derives an IV from the root IV plus extent number and runs CBC encrypt/decrypt through `crypt_scatterlist()`.

Filename encryption flows through `ecryptfs_encrypt_and_encode_filename()`. With global filename encryption enabled, it creates a tag 70 packet via `ecryptfs_write_tag_70_packet()`, then encodes the binary packet with portable filename characters and the `ECRYPTFS_FNEK_ENCRYPTED.` prefix. Decode reverses that path, rejecting non-prefixed names except dot entries and encrypted-view/passthrough cases.

## State and persistence

Persistent file state is the unencrypted upper file size, eCryptfs marker, file flags, header extent size/count, and key packet set stored in the lower file header or `user.ecryptfs`. Runtime state lives in each inode's `crypt_stat`: cipher name, FEK, key size, root IV, metadata size, extent masks, flags, key signatures, and crypto transform. Module-wide cached key TFMs persist until `ecryptfs_destroy_crypto()` at unload.

The persistent lower layout changes with `ECRYPTFS_METADATA_IN_XATTR`: when unset, encrypted data starts after the metadata header; when set, lower data starts at offset 0 and metadata is externalized to the xattr. `ECRYPTFS_VIEW_AS_ENCRYPTED` changes size reporting so users see the lower encrypted payload rather than decrypted logical size.

## Dependencies and integration points

This file depends on Linux Crypto API `skcipher`, MD5 helpers, key/xattr APIs, scatterlists, folios/pages, unaligned big-endian accessors, and lower I/O helpers declared in `ecryptfs_kernel.h`. It calls into `keystore.c` for key packet generation/parsing and tag 70 filename packets. It is called by `file.c` during open metadata initialization, by `inode.c` during lookup, create, truncate, symlink, and name translation, and by mmap/read-write paths for encrypted page traffic.

## Risks

The file contains several security-sensitive legacy choices: MD5-derived IVs, CBC mode without modern authenticated encryption, and verbose debug paths that can dump keys when `ecryptfs_verbosity > 0`. Metadata parsing must reject malformed header sizes and packet boundaries; mistakes can mis-size lower offsets or treat plaintext as encrypted. Filename decoding silently masks some `-EINVAL` cases in readdir via callers, so mixed plaintext/encrypted lower directories need careful behavior tests. Crypto transform caching is protected by mutexes, but every caller must respect `key_tfm_list_mutex` and per-TFM mutex ownership.

## Test signals

Useful tests include mounting with header metadata and xattr metadata, creating files and validating lower offsets/sizes, reading files across page and extent boundaries, truncate growth/shrink with metadata size rewrites, encrypted-view size reporting, filename encryption round trips including dot entries and malformed prefixes, unsupported cipher/key-size rejection, missing key behavior, and module unload cleanup of cached TFMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/debug.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/debug.c

## Purpose

`debug.c` contains eCryptfs-only debug printers. It does not participate in filesystem behavior except when other code paths ask it to dump authentication tokens or raw bytes for diagnosis. Its outputs are intentionally gated by `ecryptfs_verbosity`, but when enabled they can expose cryptographic material.

## Important APIs, types, and functions

The file exports `ecryptfs_dump_auth_tok()` and `ecryptfs_dump_hex()`. `ecryptfs_dump_auth_tok()` understands `struct ecryptfs_auth_tok`, password-token salt/signature fields, persistent password flags, private-key token identification, and `session_key` flags such as decrypted key, encrypted key, userspace decrypt request, and userspace encrypt request. `ecryptfs_dump_hex()` wraps `print_hex_dump()` with the `ecryptfs:` prefix and prints only when verbosity is at least 1.

## Control flow

Callers pass an auth token to `ecryptfs_dump_auth_tok()`. The function emits token type, password salt and signature for passphrase tokens, then reports session-key flags and optionally dumps decrypted or encrypted key buffers. It uses `ecryptfs_to_hex()` for salt formatting and `ecryptfs_printk()` for level-aware logging. `ecryptfs_dump_hex()` exits immediately unless `ecryptfs_verbosity >= 1`, then prints a 16-byte-row hex dump.

## State and persistence behavior

No persistent state is modified. The only state read is the passed token/buffer plus the global `ecryptfs_verbosity`. The file can leak transient secrets to persistent kernel logs when verbosity is enabled, especially FEKs, encrypted session keys, and session-key-encryption keys passed by callers in crypto and keystore code.

## Dependencies and integration points

The file depends on `ecryptfs_kernel.h`, Linux string helpers, `print_hex_dump()`, and constants from the eCryptfs public auth-token ABI. It is called from verbose paths in `crypto.c` and `keystore.c`, including FEK generation/decryption, IV derivation, key packet parsing, and candidate auth-token matching.

## Risks

The core risk is operational: enabling verbosity writes sensitive values to syslog. The implementation also uses a flag check against `auth_tok->flags & ECRYPTFS_PRIVATE_KEY`, while token type is usually represented through `auth_tok->token_type`; tests should ensure the printed type remains accurate for the ABI in use. Because this is debug-only, error handling is intentionally minimal.

## Test signals

Signals include booting/loading with default verbosity and confirming no hex dumps, setting `ecryptfs_verbosity=1` and exercising mount/open/key lookup paths, verifying password tokens print salt/signature while private-key tokens do not read password-only fields, and checking that dumps are absent in normal production logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/dentry.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/dentry.c

## Purpose

`dentry.c` provides eCryptfs dentry operations. It keeps upper dentries synchronized with lower dentry validity and releases the lower dentry reference stored in `d_fsdata`. This is the dcache glue that lets eCryptfs remain a stacked filesystem while deferring authoritative object validity to the lower filesystem when needed.

## Important APIs, types, and functions

The file defines `ecryptfs_d_revalidate()`, `ecryptfs_d_release()`, and exports `const struct dentry_operations ecryptfs_dops`. `ecryptfs_d_revalidate()` is the primary operation installed as `.d_revalidate`; `ecryptfs_d_release()` is installed as `.d_release`.

## Control flow

On dcache revalidation, the VFS calls `ecryptfs_d_revalidate()`. RCU lookup is not handled directly and returns `-ECHILD`. For non-RCU lookup, the function obtains the lower dentry from `ecryptfs_dentry_to_lower()`. If the lower dentry has `DCACHE_OP_REVALIDATE`, it snapshots the lower name and invokes the lower filesystem's `d_revalidate()` using the lower parent inode. For positive upper dentries it copies all lower inode attributes to the upper inode and invalidates the upper dentry when the upper inode has zero links.

On final dentry release, `ecryptfs_d_release()` simply `dput()`s the lower dentry reference held in `d_fsdata`.

## State and persistence behavior

The file does not define on-disk state. Runtime state is the upper dentry's `d_fsdata` pointer, which stores the lower dentry reference established during lookup or root mount setup. Revalidation refreshes upper inode metadata from lower inode metadata but does not persist data itself.

## Dependencies and integration points

This file depends on VFS dentry APIs, lower inode accessors from `ecryptfs_kernel.h`, `fsstack_copy_attr_all()`, and lower filesystem dentry operations. `main.c` installs `ecryptfs_dops` as the default dentry operations for the eCryptfs superblock. `inode.c` populates each upper dentry's lower dentry with `ecryptfs_set_dentry_lower()` during lookup and mount setup.

## Risks

Correct reference ownership is critical: every `d_fsdata` lower dentry must be a valid reference because release unconditionally `dput()`s it. Revalidation uses name snapshots to call lower operations, but behavior depends on lower filesystems honoring their own locking and lookup semantics. Returning stale-positive dentries after lower unlink would corrupt metadata visibility, so the zero-link invalidation path is an important regression point.

## Test signals

Tests should cover lookup cache hits against lower filesystems with and without `d_revalidate`, lower unlink followed by upper lookup/stat, RCU path fallback, mount/unmount dentry release reference balance, and attribute propagation after lower chmod/chown/timestamp changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/dentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/ecryptfs_kernel.h -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/ecryptfs_kernel.h

## Purpose

`ecryptfs_kernel.h` is the internal contract for the eCryptfs kernel module. It centralizes constants for the persistent file format, packet types, mount flags, per-inode crypto state, lower-object accessors, operation-table declarations, slab-cache globals, messaging structures, and cross-file function prototypes.

## Important APIs, types, and functions

Important constants include default IV and extent sizes, minimum header extent size, message buffer defaults, `ECRYPTFS_XATTR_NAME`, maximum key/cipher limits, the magic marker, file-size and marker byte counts, default cipher/key bytes, OpenPGP-inspired tag IDs 1/3/11 and eCryptfs tags 64-73, encrypted filename prefixes, and the versioning feature mask.

Core structures are `struct ecryptfs_crypt_stat`, `struct ecryptfs_inode_info`, `struct ecryptfs_mount_crypt_stat`, `struct ecryptfs_sb_info`, `struct ecryptfs_file_info`, `struct ecryptfs_global_auth_tok`, `struct ecryptfs_key_tfm`, `struct ecryptfs_message`, `struct ecryptfs_msg_ctx`, and `struct ecryptfs_daemon`. Inline helpers expose private data and lower-layer objects: `ecryptfs_file_to_lower()`, `ecryptfs_inode_to_lower()`, `ecryptfs_superblock_to_lower()`, `ecryptfs_dentry_to_lower()`, and `ecryptfs_lower_path()`. It also wraps key payload extraction for user and encrypted key types.

## Control flow

The header has no independent runtime control flow, but it shapes all eCryptfs paths. Mount code fills `ecryptfs_mount_crypt_stat`; inode allocation embeds `ecryptfs_inode_info`; open paths fill `ecryptfs_file_info`; crypto paths mutate `ecryptfs_crypt_stat`; messaging paths allocate `ecryptfs_msg_ctx` and `ecryptfs_daemon`; operation tables exported by `file.c`, `inode.c`, `dentry.c`, `super.c`, and `mmap.c` are declared here for setup in `main.c` and inode interposition.

## State and persistence behavior

The header defines the meaning of persistent metadata flags and packet tags. `ECRYPTFS_METADATA_IN_XATTR`, `ECRYPTFS_VIEW_AS_ENCRYPTED`, `ECRYPTFS_ENCRYPT_FILENAMES`, and related flags determine whether metadata lives in the lower header or xattr, how upper sizes are calculated, and how lower filenames are transformed. It also defines runtime-only state flags such as `ECRYPTFS_KEY_VALID`, `ECRYPTFS_KEY_SET`, and `ECRYPTFS_I_SIZE_INITIALIZED`.

## Dependencies and integration points

The header depends on kernel crypto, key, VFS, fs_stack, namespace, backing-device, scatterlist, hash, and public `linux/ecryptfs.h` definitions. It integrates every source file in the eCryptfs directory: crypto, keystore, inode, file, mmap, read/write, superblock, miscdev, messaging, kthread, debug, and main.

## Risks

Because this file is a shared ABI inside the module, flag-value changes can corrupt interoperability with existing encrypted files or userspace tools. Structure layout assumptions also interact with slab caches and key payload data. Inline lower-object accessors assume `private_data`, `d_fsdata`, and `s_fs_info` are initialized; calling them early or after release can crash. Compile-time messaging stubs return `-ENOTCONN` or `-ENOMSG`, so public-key operations must handle messaging-disabled builds.

## Test signals

Signals include building with and without `CONFIG_ECRYPT_FS_MESSAGING` and `CONFIG_ENCRYPTED_KEYS`, mounting with every supported flag combination, validating version mask export, exercising lower-object accessors through lookup/open/release/unmount, and running old-file compatibility tests that prove constants and flag mappings remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/ecryptfs_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/file.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/file.c

## Purpose

`file.c` implements eCryptfs file operations for regular files and directories. It opens and releases lower files, initializes or reads encryption metadata at open time, forwards generic reads/writes/mmap/fsync/ioctl/fasync behavior to lower or generic VFS helpers, and translates encrypted lower directory names back to upper plaintext names during readdir.

## Important APIs, types, and functions

The exported operation tables are `ecryptfs_dir_fops` and `ecryptfs_main_fops`. Important functions include `ecryptfs_read_update_atime()`, `ecryptfs_splice_read_update_atime()`, `ecryptfs_readdir()`, `ecryptfs_filldir()`, `read_or_initialize_metadata()`, `ecryptfs_open()`, `ecryptfs_dir_open()`, `ecryptfs_flush()`, `ecryptfs_release()`, `ecryptfs_dir_release()`, `ecryptfs_fsync()`, and ioctl forwarding helpers. `struct ecryptfs_getdents_callback` wraps a lower `dir_context` with upper caller state.

## Control flow

Regular open allocates `struct ecryptfs_file_info`, marks policy as applied/encrypted if not already set, obtains the per-inode lower file through `ecryptfs_get_lower_file()`, rejects writable upper opens when the cached lower file is read-only, stores the lower file in upper private data, and calls `read_or_initialize_metadata()`. Metadata initialization first returns early when policy and key are already valid, otherwise calls `ecryptfs_read_metadata()`. If metadata read fails and plaintext passthrough is enabled, it clears encrypted state. If the lower file is empty and header metadata mode is active, it calls `ecryptfs_initialize_file()` to write a new header.

Directory open allocates file private data and opens the lower path directly with current credentials. Directory readdir calls `iterate_dir()` on the lower file with `ecryptfs_filldir()` as the actor. Each lower name is decoded/decrypted through `ecryptfs_decode_and_decrypt_filename()` before being emitted to the upper caller; malformed plaintext lower names under filename encryption are skipped/masked for common mixed-directory cases.

Regular reads use generic page-cache reads plus lower atime updates. Writes use `generic_file_write_iter()`, relying on eCryptfs address-space operations in `mmap.c` and lower I/O helpers for encryption. `fsync`, `flush`, selected ioctls, compat ioctls, and fasync are forwarded to the lower file when supported.

## State and persistence behavior

The file owns per-open `struct ecryptfs_file_info` and references the per-inode cached lower file. Persistent changes happen indirectly through metadata initialization and writeback, not through this file alone. It synchronizes lower atime after successful upper reads and copies lower attributes after selected ioctls.

## Dependencies and integration points

It depends on generic VFS file helpers, lower path helpers from `ecryptfs_kernel.h`, metadata and filename functions from `crypto.c`, inode initialization from `inode.c`, lower-file lifetime functions from `main.c`, and address-space operations declared externally. Inode interposition in `inode.c` installs these operation tables based on file type.

## Risks

Open-time metadata failures determine whether a file is usable, initialized, or treated as plaintext passthrough; regressions here can either deny valid files or expose plaintext unexpectedly. Directory listing intentionally masks some filename-decode errors, so tests must distinguish harmless lower plaintext names from real corruption. Lower file reference counting must remain balanced between `ecryptfs_get_lower_file()` and release. Ioctl forwarding is intentionally restricted; adding commands can expose lower filesystem behavior not meaningful for encrypted upper files.

## Test signals

Tests should cover regular open for existing encrypted files, empty-file initialization, plaintext passthrough mounts, read-only lower mounts, directory listing with encrypted names, mixed lower plaintext entries, read/splice atime propagation, fsync/flush forwarding, selected ioctls, mmap support rejection when lower mmap is unavailable, and lower file reference cleanup on failed opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/inode.c

## Purpose

`inode.c` implements eCryptfs inode operations and most namespace manipulation. It interposes upper inodes over lower inodes, maps plaintext names to encrypted lower names during lookup/create/symlink, initializes new encrypted files, handles link/unlink/mkdir/rmdir/mknod/rename, translates symlink targets, manages truncate and setattr sizing across encrypted headers, and forwards xattr, ACL, permission, and file-attribute operations.

## Important APIs, types, and functions

Externally visible functions are `ecryptfs_get_inode()`, `ecryptfs_initialize_file()`, `ecryptfs_truncate()`, `ecryptfs_setxattr()`, and `ecryptfs_getxattr_lower()`. The exported operation tables are `ecryptfs_symlink_iops`, `ecryptfs_dir_iops`, `ecryptfs_main_iops`, and `ecryptfs_xattr_handlers`. Key internal functions include `__ecryptfs_get_inode()`, `ecryptfs_inode_set()`, `ecryptfs_lookup()`, `ecryptfs_lookup_interpose()`, `ecryptfs_create()`, `ecryptfs_do_create()`, `ecryptfs_i_size_read()`, `ecryptfs_symlink()`, `ecryptfs_readlink_lower()`, `upper_size_to_lower_size()`, `__ecryptfs_truncate()`, and `ecryptfs_setattr()`.

## Control flow

Lookup encrypts the requested upper name when mount-wide filename encryption is enabled, then performs `lookup_noperm_unlocked()` in the lower parent. `ecryptfs_lookup_interpose()` stores the lower dentry, obtains or creates an upper inode using `iget5_locked()`, and for regular files reads enough metadata to initialize upper size. Inode setup copies lower attributes, sets operation tables by type, initializes special inodes when needed, and rejects lower files from unrelated lower superblocks or casefolded directories.

Create first creates the lower file, interposes the upper inode, then calls `ecryptfs_initialize_file()` to generate a new FEK and write eCryptfs metadata. Failure after lower creation unlinks the lower file and fails the new inode. Symlink creation encrypts/encodes the symlink target string with the same filename mechanism before calling lower `vfs_symlink()`. Directory and special-file operations mostly forward to lower VFS helpers and copy attributes back up.

Truncate converts upper logical sizes to lower physical sizes by adding header size and rounding to extents. Growing writes a single zero at the new final byte so write paths fill intermediate encrypted zeros. Shrinking zeros the remainder of the final page, updates the encrypted metadata i_size, then possibly truncates the lower inode. `setattr` ensures metadata is read and keys are valid before size changes, with passthrough fallback only when configured.

## State and persistence behavior

Persistent effects include lower namespace changes, eCryptfs header creation, lower encrypted symlink names, xattr writes/removals, ACL updates, file-attribute updates, and metadata i_size rewrites on truncate. Runtime state includes upper inode references to lower inodes, dentry lower pointers, crypt_stat initialization, and copied lower inode attributes.

## Dependencies and integration points

The file depends on VFS namei, fs_stack, xattr, ACL, fileattr, unaligned access, crypto metadata functions, lower file lifetime from `main.c`, file operation tables from `file.c`, dentry operations from `dentry.c`, and address-space operations from `mmap.c`. It is central to mount-root setup in `main.c` and to all upper filesystem operations.

## Risks

Size translation is security- and data-integrity-sensitive; off-by-one errors can truncate ciphertext, leak stale tail bytes, or corrupt header metadata. Filename encryption during lookup and symlink target creation must match readdir/readlink decoding exactly. Lower namespace locking uses modern start/end dentry helpers; regressions can race with concurrent lower changes. Passthrough mode changes failure handling for invalid metadata and needs careful coverage.

## Test signals

Tests should include lookup of encrypted and plaintext lower names, create rollback after metadata write failure, hard link size preservation, symlink target round trip, mkdir/rmdir/mknod/rename behavior, truncate grow and shrink across page/extent boundaries, xattr and ACL forwarding, fileattr forwarding, casefold lower directory rejection, lower attribute propagation, and passthrough versus non-passthrough invalid-header behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/keystore.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/keystore.c

## Purpose

`keystore.c` implements eCryptfs key-packet parsing and generation. It translates between persistent OpenPGP-inspired metadata packets, kernel keyring auth tokens, FEK encryption/decryption, public-key daemon callouts, and FNEK filename packets. It is the policy enforcement point for which mount/auth tokens can unlock or wrap a file encryption key.

## Important APIs, types, and functions

Exported functions include `ecryptfs_parse_packet_length()`, `ecryptfs_write_packet_length()`, `ecryptfs_keyring_auth_tok_for_sig()`, `ecryptfs_parse_packet_set()`, `ecryptfs_generate_key_packet_set()`, `ecryptfs_add_keysig()`, `ecryptfs_add_global_auth_tok()`, `ecryptfs_write_tag_70_packet()`, and `ecryptfs_parse_tag_70_packet()`.

Important packet helpers handle tag 1 public-key encrypted FEKs, tag 3 passphrase encrypted FEKs, tag 11 literal signature packets, tag 64/65/66/67 userspace-daemon messages, and tag 70 FNEK-encrypted filenames. Helper structs named `*_silly_stack` move large temporary state off the kernel stack for tag 70 operations.

## Control flow

For existing files, `ecryptfs_parse_packet_set()` walks metadata packets until a non-auth-token packet appears. Tag 3 packets produce password candidate tokens and must be followed by a tag 11 literal packet containing the auth-token signature. Tag 1 packets produce private-key candidate tokens. The function then searches mount-wide tokens first, optionally falls back to the user keyring, copies the matching secret material into the candidate token, decrypts the FEK via passphrase or PKI flow, computes the root IV, and initializes the crypt context. Failed candidates are removed and the next matching token is tried.

For new files, `ecryptfs_generate_key_packet_set()` iterates inode key signatures. For password tokens it writes a tag 3 packet containing the FEK encrypted by the session-key-encryption key, followed by a tag 11 signature packet. For private-key tokens it writes a tag 1 packet, potentially using ecryptfsd through tag 66 request and tag 67 response to encrypt the FEK. A boundary byte terminates the packet set.

Filename encryption uses tag 70. `ecryptfs_write_tag_70_packet()` finds the FNEK auth token, pads the plaintext name with deterministic non-null bytes derived from MD5 over the FNEK material, encrypts with the filename cipher and zero IV, and writes FNEK signature, cipher code, and encrypted name. `ecryptfs_parse_tag_70_packet()` validates size, resolves the FNEK token, decrypts, finds the null separator, and returns the plaintext suffix.

## State and persistence behavior

Persistent state is the packet set embedded in the lower file header or xattr and encrypted filename tag 70 packets embedded in lower dentry names. Runtime state includes mount-wide global auth-token references, per-inode key signature lists, per-call auth token candidate lists, and keyring references locked through key semaphores. Invalid global tokens are flagged and their key references dropped.

## Dependencies and integration points

The file depends on Linux keyrings, encrypted/user key payloads, skcipher, scatterlists, random/MD5 support, messaging APIs for ecryptfsd, and constants/types from `ecryptfs_kernel.h`. It is called by `crypto.c` for metadata and filename operations, by `main.c` while registering mount auth tokens, and by public-key flows through `messaging.c`/`miscdev.c`.

## Risks

This is a high-risk parser and key-management file. Packet length handling, maximum sizes, signature matching, and key semaphore lifetime must be correct. Legacy crypto choices include MD5, OpenPGP S2K MD5, CBC/ECB-like FEK wrapping paths, and unauthenticated packet contents. Verbose logging can dump secret material. Public-key support depends on a live userspace daemon for the caller's euid; timeouts and malformed daemon responses must fail closed.

## Test signals

Tests should cover packet length one-byte/two-byte boundaries and rejection of unsupported five-byte lengths, valid/invalid tag 1, 3, 11, 65, 67, and 70 packets, multiple key signatures with first-candidate failure fallback, missing/expired/revoked key errors, `ECRYPTFS_GLOBAL_MOUNT_AUTH_TOK_ONLY`, password and private-key mount flows, filename encryption/decryption round trips, malformed separator and oversize filename rejection, and messaging-disabled public-key failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/keystore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/kthread.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/kthread.c

## Purpose

`kthread.c` provides the eCryptfs helper kernel thread used to open lower files with read-write access when a direct open by the caller fails. This lets eCryptfs maintain a single lower file per upper inode and still obtain write-capable lower access for encrypted writeback when permitted.

## Important APIs, types, and functions

The file defines `struct ecryptfs_open_req`, static `ecryptfs_kthread_ctl`, and static `ecryptfs_kthread`. Exported functions are `ecryptfs_init_kthread()`, `ecryptfs_destroy_kthread()`, and `ecryptfs_privileged_open()`. The worker body is `ecryptfs_threadfn()`.

## Control flow

Initialization sets up the request-list mutex, waitqueue, and list head, then starts `ecryptfs-kthread`. The thread waits in a freezable wait loop until requests arrive or shutdown is requested. Each request contains a lower path, result pointer, completion, and list node. The thread removes requests from the queue, opens the lower path with `O_RDWR | O_LARGEFILE` using current credentials, stores the resulting `struct file *` or error pointer, and completes the request.

`ecryptfs_privileged_open()` first tries `dentry_open()` directly with `O_RDONLY` when the lower inode is read-only, otherwise `O_RDWR`. If direct read-write open fails, it queues a request to the helper thread, wakes it, and waits for completion. During shutdown, new requests are rejected and queued requests are completed with `ERR_PTR(-EIO)`.

## State and persistence behavior

There is no on-disk state. Runtime state is the global kthread, a guarded request queue, a zombie flag, and per-request completions. Successful opens create lower file references that are later closed by `ecryptfs_put_lower_file()` or directory release paths.

## Dependencies and integration points

The file depends on kthread, freezer, waitqueue, completion, mount/path, and VFS open APIs. `main.c` initializes and destroys the kthread at module load/unload. `main.c` lower-file lifetime code calls `ecryptfs_privileged_open()` through `ecryptfs_init_lower_file()`.

## Risks

Credential context is subtle: direct open uses the caller's supplied credentials, while queued opens occur in the helper thread using its current credentials. The request's `cred` parameter is not used in the queued path, which is intentional historical behavior but sensitive. Shutdown ordering must complete all queued requests before `kthread_stop()` to avoid waiters hanging. File reference ownership comments require matching `fput()` on lower-file release.

## Test signals

Signals include successful direct read-only and read-write lower opens, fallback queued open after direct write-open denial, concurrent opens on the same inode, module unload with pending requests, freezer interaction during suspend, and reference cleanup after open failure or delayed success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/kthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/main.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/main.c

## Purpose

`main.c` owns module parameters, mount option parsing, filesystem registration, superblock setup, lower-file lifetime management, slab cache lifecycle, sysfs version export, and module init/exit sequencing. It is the top-level integration point that turns eCryptfs operation tables and crypto/key machinery into a mountable stacked filesystem.

## Important APIs, types, and functions

Important exported globals are `ecryptfs_verbosity`, `ecryptfs_message_buf_len`, `ecryptfs_message_wait_timeout`, and `ecryptfs_number_of_users`. Important functions include `__ecryptfs_printk()`, `ecryptfs_get_lower_file()`, `ecryptfs_put_lower_file()`, `ecryptfs_parse_param()`, `ecryptfs_validate_options()`, `ecryptfs_get_tree()`, `ecryptfs_init_fs_context()`, `ecryptfs_kill_block_super()`, `ecryptfs_init_kmem_caches()`, `ecryptfs_free_kmem_caches()`, `do_sysfs_registration()`, `ecryptfs_init()`, and `ecryptfs_exit()`.

The mount parser recognizes `sig`, `ecryptfs_sig`, cipher options, key-byte options, passthrough, xattr metadata, encrypted view, FNEK signature, filename cipher/key bytes, unlink sigs, mount-auth-token-only, and check-dev-ruid.

## Control flow

Mount context initialization allocates `struct ecryptfs_fs_context` and `struct ecryptfs_sb_info`, initializes mount crypto state, and installs `ecryptfs_context_ops`. Each parsed mount parameter mutates mount crypto state or context booleans. Validation requires at least one auth-token signature, fills default ciphers/key sizes, validates cipher support, initializes cached key TFMs, and resolves global auth tokens from the keyring.

`ecryptfs_get_tree()` validates the source, rejects FIPS mode, allocates an anonymous superblock, installs super/xattr/dentry operations, resolves the lower directory path, rejects stacking on eCryptfs and idmapped lower mounts, optionally checks lower root uid against the mounting user, mirrors lower superblock flags, forces read-only for lower read-only or encrypted-view mounts, checks stack depth, interposes the root inode, stores lower root dentry and mount, and returns the root.

Lower-file lifetime uses an atomic per-inode count plus mutex. First `ecryptfs_get_lower_file()` opens a lower file with `ecryptfs_privileged_open()`; final `ecryptfs_put_lower_file()` waits for upper writeback, closes the lower file, and clears the pointer.

Module init checks extent size against page size, creates all slabs, registers sysfs `/sys/fs/ecryptfs/version`, starts the helper kthread, initializes messaging, initializes crypto, and registers the filesystem. Exit reverses those steps.

## State and persistence behavior

Persistent filesystem state is not written directly here, but mount options determine all later metadata placement, filename encryption, and passthrough semantics. Runtime state includes mount-wide auth-token lists, lower mount reference, slab caches, sysfs kobject, cached lower files per inode, and module parameters that affect logging and messaging capacity/timeouts.

## Dependencies and integration points

The file depends on fs_context/fs_parser, keyrings, FIPS status, path lookup, stacked filesystem helpers, sysfs, slab, module registration, and all eCryptfs operation tables and init functions. It coordinates `crypto.c`, `keystore.c`, `messaging.c`, `kthread.c`, `super.c`, `inode.c`, `file.c`, and `dentry.c`.

## Risks

Mount option validation is security critical because missing or invalid auth tokens should fail before files are exposed. Encrypted-view forces read-only; missing that would allow writes through a ciphertext view. Lower-file refcount imbalance can leak files or close them under active I/O. Init/exit order must match dependency order, especially messaging before public-key operations and slab caches before object allocation. FIPS mode disables the module because the implementation uses non-FIPS-approved primitives.

## Test signals

Tests should cover all mount options and aliases, missing sig rejection, invalid cipher/key-size rejection, FNEK filename mount validation, xattr and encrypted-view flag effects, check-dev-ruid permissions, lower read-only propagation, FIPS rejection, eCryptfs-on-eCryptfs rejection, idmapped lower mount rejection, stack-depth checks, sysfs version contents, lower-file refcount open/release behavior, and init failure unwinding at each stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/messaging.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/messaging.c

## Purpose

`messaging.c` implements the kernel side of request/response messaging between eCryptfs and the per-user `ecryptfsd` userspace daemon. It manages message context allocation, daemon lookup by effective uid, daemon lifetime, response delivery, wait timeouts, and messaging subsystem initialization/release. It is used primarily for public-key operations in `keystore.c`.

## Important APIs, types, and functions

Exported functions are `ecryptfs_msg_ctx_alloc_to_free()`, `ecryptfs_find_daemon_by_euid()`, `ecryptfs_spawn_daemon()`, `ecryptfs_exorcise_daemon()`, `ecryptfs_process_response()`, `ecryptfs_send_message()`, `ecryptfs_wait_for_response()`, `ecryptfs_init_messaging()`, and `ecryptfs_release_messaging()`. Internal state includes `ecryptfs_msg_ctx_free_list`, `ecryptfs_msg_ctx_alloc_list`, `ecryptfs_msg_ctx_lists_mux`, `ecryptfs_daemon_hash`, `ecryptfs_daemon_hash_mux`, `ecryptfs_hash_bits`, `ecryptfs_msg_counter`, and `ecryptfs_msg_ctx_arr`.

## Control flow

Initialization sizes a daemon hash table from `ecryptfs_number_of_users`, initializes every hash head, allocates `ecryptfs_message_buf_len` message contexts, puts them all on the free list, then registers the misc device through `ecryptfs_init_ecryptfs_miscdev()`.

Sending a message locks the daemon hash, finds a daemon for the caller's current euid, acquires a free message context, moves it to the allocated list, assigns a monotonically increasing counter, and queues the request to the daemon with `ecryptfs_send_miscdev()`. Waiting sleeps interruptibly until the context state becomes `DONE` or timeout expires. On success it detaches the response message for the caller; in all cases it returns the context to the free list.

Responses enter through miscdev write handling and call `ecryptfs_process_response()`. The function validates the response index, verifies the context is pending, checks the sequence counter, duplicates the response into the context, marks the context done, and wakes the blocked task.

Daemon lifecycle starts with `ecryptfs_spawn_daemon()`, which allocates a daemon for the miscdev file and inserts it in the euid hash. `ecryptfs_exorcise_daemon()` refuses to destroy daemons in read/poll, drops queued outgoing messages, removes the hash node, and frees sensitive daemon memory.

## State and persistence behavior

There is no disk persistence. Runtime state is bounded by module parameters: daemon hash entries by euid, fixed-size message context array, free/allocated lists, per-daemon outgoing queues, wait queues, task pointers, and response buffers. Message counters are sequence numbers used to reject stale or mismatched daemon responses.

## Dependencies and integration points

The file depends on scheduler sleeps, mutexes, hash lists, uid helpers, slab allocation, and miscdev functions declared in `ecryptfs_kernel.h` and implemented in `miscdev.c`. `keystore.c` uses `ecryptfs_send_message()` and `ecryptfs_wait_for_response()` for public-key FEK encrypt/decrypt. `main.c` initializes and releases messaging during module lifecycle.

## Risks

The fixed message context pool can exhaust and fail public-key operations. Wait semantics use `schedule_timeout_interruptible()` without an explicit condition waitqueue, relying on `wake_up_process()` from response delivery; signal and timeout behavior need careful testing. Sequence checking protects against response misdelivery, but context reuse after timeout must remain safe. Daemon teardown drops queued messages and returns contexts to free state, so races with miscdev reads/writes are a key risk.

## Test signals

Tests should cover daemon registration per euid, duplicate daemon open rejection, message send without daemon returning `-ENOTCONN`, context pool exhaustion, valid response delivery, wrong index and wrong sequence rejection, timeout returning `-ENOMSG`, daemon release with queued requests, module unload cleanup, and public-key keystore operations through a real or mocked `ecryptfsd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/messaging.c -->
