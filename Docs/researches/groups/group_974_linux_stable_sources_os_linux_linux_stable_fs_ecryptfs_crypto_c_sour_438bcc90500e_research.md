# Group Research: group_974_linux_stable_sources_os_linux_linux_stable_fs_ecryptfs_crypto_c_sour_438bcc90500e

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/crypto.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/crypto.c

## Summary
Implements eCryptfs cryptographic data handling: per-file crypto context setup, page/extent encryption and decryption, header and xattr metadata read/write, cipher code mapping, cached key transform management, and encrypted filename encode/decode support.

## Main Responsibilities
- Initialize and destroy per-inode `ecryptfs_crypt_stat` and mount-wide crypt state.
- Derive root IVs from file encryption keys and per-extent IVs from root IV plus extent offset.
- Encrypt and decrypt page contents one extent at a time using Linux Crypto API `skcipher` transforms.
- Read and write eCryptfs metadata from lower file headers or `user.ecryptfs` xattrs.
- Generate new file encryption keys and propagate mount-wide policy flags/signatures into inode crypt state.
- Validate eCryptfs file markers, parse/write file flags, and handle legacy version-0 header defaults.
- Map RFC2440 cipher codes to kernel cipher names and AES key sizes.
- Maintain a module-wide cache of key-encryption cipher transforms.
- Encrypt, encode, decode, and decrypt lower filenames using tag-70 FNEK packets and portable filename characters.
- Compute the effective encrypted-name maximum accepted through `ecryptfs_set_f_namelen()`.

## Key APIs
- `ecryptfs_new_file_context()`: creates a new encrypted file context, copies mount signatures, generates a FEK, and initializes the cipher.
- `ecryptfs_encrypt_page()` / `ecryptfs_decrypt_page()`: translate upper folios to lower encrypted page data.
- `ecryptfs_write_metadata()` / `ecryptfs_read_metadata()`: write or discover eCryptfs metadata in file contents or xattrs.
- `ecryptfs_read_and_validate_header_region()` / `ecryptfs_read_and_validate_xattr_region()`: lightweight marker checks and `i_size` initialization.
- `ecryptfs_encrypt_and_encode_filename()` / `ecryptfs_decode_and_decrypt_filename()`: dentry-name translation for filename encryption.
- `ecryptfs_get_tfm_and_mutex_for_cipher_name()`: shared transform lookup/creation for key and filename crypto.

## Important Behavior
Data encryption uses CBC-mode transforms named as `cbc(<cipher>)`, with the file FEK set lazily on the per-inode transform. Each page is split into `crypt_stat->extent_size` extents, and IVs are MD5-derived from the root IV and extent number.

Metadata layout starts with an unencrypted file-size field, an 8-byte randomized eCryptfs marker pair, flags/version, header extent metadata, and an authentication-token packet set. If xattr metadata is enabled, the lower file data starts at offset zero; otherwise `metadata_size` is reserved at the front of the lower file.

Filename encryption is only implemented for mount-wide FNEK mode in this file. It delegates packet construction/parsing to `keystore.c`, then applies a custom 6-bit portable alphabet and the `ECRYPTFS_FNEK_ENCRYPTED.` prefix for lower dentry names.

## Research Notes
This file is the central bridge between VFS/page-cache operations and eCryptfs' on-disk crypto format. Correctness depends on metadata location flags, extent-size calculations, matching cipher/key-size negotiation, and key availability before any encrypted file or filename path is processed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/debug.c

## Summary
Provides debug-only helpers for printing eCryptfs authentication-token details and raw hex dumps under the module verbosity setting.

## Main Responsibilities
- Dump authentication token type, salt, signature, persistence flag, and session-key state.
- Print decrypted or encrypted session-key bytes only when `ecryptfs_verbosity > 0`.
- Provide `ecryptfs_dump_hex()` as the common hex-dump helper used by crypto and keystore code.

## Key APIs
- `ecryptfs_dump_auth_tok()`
- `ecryptfs_dump_hex()`

## Important Behavior
The functions can expose secret key material to the kernel log when verbosity is enabled. `main.c` warns at module init when `ecryptfs_verbosity > 0` because these debug paths can print sensitive values.

## Research Notes
This file has no state of its own. It is purely diagnostic, but security-sensitive because it can log decrypted keys.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/dentry.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/dentry.c

## Summary
Defines eCryptfs dentry operations for revalidating upper dentries against lower dentries and releasing lower dentry references.

## Main Responsibilities
- Reject RCU pathwalk revalidation with `-ECHILD`.
- Delegate revalidation to the lower dentry when the lower filesystem supplies `d_revalidate`.
- Refresh upper inode attributes from the lower inode for positive dentries.
- Invalidate upper dentries whose inode link count dropped to zero.
- Drop the lower dentry reference stored in `dentry->d_fsdata`.

## Key APIs
- `ecryptfs_d_revalidate()`
- `ecryptfs_d_release()`
- `ecryptfs_dops`

## Important Behavior
The revalidation path snapshots the lower dentry name before invoking the lower filesystem operation. For positive upper dentries, it mirrors lower attributes and returns invalid when the upper inode has no links.

## Research Notes
This file is small but part of the stackable-filesystem contract: every eCryptfs dentry owns a referenced lower dentry in `d_fsdata`, and dentry validity follows the lower filesystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/ecryptfs_kernel.h -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/ecryptfs_kernel.h

## Summary
Shared internal header for eCryptfs. It defines constants, metadata packet tags, core private structures, inline accessors linking upper and lower objects, optional messaging stubs, cache externs, operation-table externs, and internal function prototypes.

## Main Responsibilities
- Define default extent, IV, message, xattr, cipher, key, marker, filename, and packet-size constants.
- Define eCryptfs packet tags for RFC2440-inspired key packets and filename-encryption packets.
- Define cryptographic state structures including `ecryptfs_crypt_stat`, `ecryptfs_mount_crypt_stat`, `ecryptfs_key_sig`, `ecryptfs_key_tfm`, and `ecryptfs_global_auth_tok`.
- Define filesystem private state: `ecryptfs_inode_info`, `ecryptfs_sb_info`, and `ecryptfs_file_info`.
- Define messaging structures for ecryptfsd integration: `ecryptfs_message`, `ecryptfs_msg_ctx`, and `ecryptfs_daemon`.
- Provide inline helpers for lower inode, dentry, superblock, path, and file mappings.
- Provide key-payload helpers for user keys and optional encrypted-key support.
- Declare eCryptfs operation tables, kmem caches, module parameters, and internal APIs.

## Key Data Structures
- `struct ecryptfs_crypt_stat`: per-inode encryption flags, file version, sizes, cipher, FEK, root IV, transform, and key signature list.
- `struct ecryptfs_mount_crypt_stat`: mount-wide auth token list, cipher defaults, FNEK settings, and mount policy flags.
- `struct ecryptfs_inode_info`: VFS inode wrapper plus lower inode, lower-file refcounting state, and crypt state.
- `struct ecryptfs_daemon` and `struct ecryptfs_msg_ctx`: userspace-daemon routing and pending response tracking.

## Important Behavior
The header centralizes flags that control major behavior: plaintext passthrough, xattr metadata, encrypted view, filename encryption, mount-auth-token-only, encrypted file state, metadata location, key validity, and initialized `i_size`.

When `CONFIG_ECRYPT_FS_MESSAGING` is disabled, messaging functions are compiled as stubs returning connection/message errors. This lets most eCryptfs code build while public-key packet operations fail cleanly without daemon support.

## Research Notes
This file is the dependency hub for the eCryptfs module. The most important invariants are upper-to-lower object ownership, metadata-size calculation through `ecryptfs_lower_header_size()`, auth-token lifetime, and matching the packet constants used by `crypto.c` and `keystore.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/ecryptfs_kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/file.c

## Summary
Implements eCryptfs file and directory operations. It opens and tracks lower files, initializes or reads encryption metadata, wraps read/readdir behavior for lower atime and filename decryption, forwards selected ioctls, and delegates mmap/fsync/flush/fasync behavior to lower files where appropriate.

## Main Responsibilities
- Wrap regular reads and splice reads so successful upper reads update lower atime.
- Implement directory iteration by decoding/decrypting lower names before emitting them.
- Open regular files, acquire the shared lower file, enforce lower read-only constraints, and load or initialize metadata.
- Open directories directly on the lower path.
- Support plaintext passthrough and empty-file initialization behavior when metadata is absent.
- Forward supported ioctls and compat ioctls to lower files: FITRIM, flags, and version ioctls.
- Synchronize writes and lower flush/fsync operations.
- Define regular-file and directory `file_operations`.

## Key APIs
- `ecryptfs_open()`
- `ecryptfs_dir_open()`
- `ecryptfs_readdir()`
- `read_or_initialize_metadata()`
- `ecryptfs_main_fops`
- `ecryptfs_dir_fops`

## Important Behavior
`read_or_initialize_metadata()` first tries to parse eCryptfs metadata. If that fails, plaintext passthrough can allow a non-encrypted lower file. If xattr metadata is not enabled and the lower file is empty, eCryptfs initializes it as an encrypted file by writing headers.

Directory reads mask `-EINVAL` filename-decryption failures, allowing plaintext lower names such as `lost+found` to be skipped rather than breaking the entire directory listing when filename encryption is enabled.

Regular file open shares a single lower `struct file` per upper inode via `ecryptfs_get_lower_file()`. Directory open uses a separate `dentry_open()` for each directory file.

## Research Notes
This file is the regular VFS file-operation layer. It relies on `crypto.c` for metadata and filename decoding, `main.c` for lower-file lifetime, and `inode.c` for upper/lower inode mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/inode.c

## Summary
Implements eCryptfs inode operations and most namespace-changing VFS behavior. It interposes upper inodes over lower inodes, translates names through filename encryption, creates and initializes encrypted files, handles unlink/link/rename/symlink/mkdir/mknod/rmdir, translates truncation sizes, and forwards xattrs, ACLs, file attributes, permissions, and getattr/setattr to the lower filesystem.

## Main Responsibilities
- Create upper inodes with `iget5_locked()` keyed by lower inode identity.
- Reject casefolded lower directories and cross-superblock lower inodes.
- Assign inode/file operation tables by inode type.
- Interpose upper dentries over existing lower dentries during lookup and creation.
- Encrypt and encode lookup names before lower lookup when filename encryption is enabled.
- Initialize new regular files with eCryptfs metadata and generated file encryption keys.
- Encode symlink targets on creation and decode/decrypt symlink targets on read.
- Delegate namespace operations to lower VFS helpers while copying back attributes.
- Convert upper file sizes to lower encrypted sizes for truncate and expansion.
- Forward permission, getattr, setattr, xattr, ACL, and fileattr operations.

## Key APIs
- `ecryptfs_get_inode()`
- `ecryptfs_lookup()`
- `ecryptfs_create()`
- `ecryptfs_initialize_file()`
- `ecryptfs_truncate()`
- `ecryptfs_setattr()`
- `ecryptfs_main_iops`
- `ecryptfs_dir_iops`
- `ecryptfs_symlink_iops`
- `ecryptfs_xattr_handlers`

## Important Behavior
Lookup sets `d_fsdata` to the lower dentry even for negative dentries. For regular files, it reads and validates header or xattr metadata early enough to initialize upper `i_size`.

Truncation is encryption-aware. Expanding writes a single zero at the new last byte so the write path fills intermediate zeros. Shrinking zeroes the tail of the final upper page, updates encrypted metadata with the new upper size, and only truncates the lower file when the encrypted lower size actually decreases.

Most metadata changes are passed to the lower inode via `notify_change()`, but size changes go through `__ecryptfs_truncate()`. Setuid/setgid kill operations intentionally let the lower filesystem interpret mode clearing.

## Research Notes
This is the main stackable inode layer. Its core invariants are stable lower inode references, dentry lower mappings, encrypted filename translation before lower lookup/creation, and careful upper-size versus lower-size conversion for encrypted regular files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/keystore.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/keystore.c

## Summary
Implements eCryptfs key management and packet handling. It parses and writes OpenPGP-inspired authentication-token packets, retrieves auth tokens from mount-wide lists or the kernel keyring, encrypts/decrypts file encryption keys, communicates with ecryptfsd for public-key operations, and implements FNEK filename packet encryption/decryption.

## Main Responsibilities
- Parse and write variable-length eCryptfs packet sizes.
- Generate and parse tag-1 public-key encrypted FEK packets.
- Generate and parse tag-3 passphrase encrypted FEK packets plus tag-11 signature literal packets.
- Generate tag-64/tag-66 requests and parse tag-65/tag-67 responses for userspace daemon public-key operations.
- Verify auth-token structure versions and token types loaded from user or encrypted keys.
- Look up auth tokens from mount-global registrations or fallback kernel keyring descriptions.
- Decrypt passphrase-encrypted FEKs in kernel with cached Crypto API transforms.
- Decrypt or encrypt public-key FEKs through ecryptfsd messaging when enabled.
- Write and parse tag-70 FNEK encrypted filename packets.
- Generate complete key packet sets for new file headers.
- Register per-file key signatures and mount-wide global auth tokens.

## Key APIs
- `ecryptfs_parse_packet_length()` / `ecryptfs_write_packet_length()`
- `ecryptfs_keyring_auth_tok_for_sig()`
- `ecryptfs_parse_packet_set()`
- `ecryptfs_generate_key_packet_set()`
- `ecryptfs_write_tag_70_packet()`
- `ecryptfs_parse_tag_70_packet()`
- `ecryptfs_add_keysig()`
- `ecryptfs_add_global_auth_tok()`

## Important Behavior
File metadata can contain multiple candidate auth-token packets. `ecryptfs_parse_packet_set()` parses all recognized auth packets, then searches for a matching usable secret. If decryption fails for one candidate, it removes that candidate and tries the next.

Passphrase packet handling uses the session-key encryption key from the auth token to decrypt the FEK with the file cipher. Public-key packet handling sends request packets to userspace and waits for response packets through the messaging subsystem.

Filename encryption with tag 70 uses the mount-wide FNEK signature, requires password auth tokens, prepends deterministic non-null bytes derived from MD5 of the session-key encryption key plus a NUL separator, encrypts the padded filename, and stores the FNEK signature and cipher code in the packet.

## Research Notes
This is the eCryptfs key and packet-format authority. Important correctness points include key semaphore lifetime, `key_put()` pairing, packet boundary checks, encrypted-key size limits, auth-token invalidation on bad payloads, and consistency with `crypto.c` metadata and filename paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/keystore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/kthread.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/kthread.c

## Summary
Provides the eCryptfs kernel thread used as a fallback path for opening lower files with read/write access when direct open under caller credentials fails.

## Main Responsibilities
- Maintain a request queue of lower-file open requests.
- Run `ecryptfs-kthread`, which processes queued `dentry_open()` requests.
- Initialize and destroy thread control state at module load/unload.
- Mark shutdown with `ECRYPTFS_KTHREAD_ZOMBIE` and complete pending requests with `-EIO`.
- Implement `ecryptfs_privileged_open()` for lower-file acquisition.

## Key APIs
- `ecryptfs_init_kthread()`
- `ecryptfs_destroy_kthread()`
- `ecryptfs_privileged_open()`

## Important Behavior
`ecryptfs_privileged_open()` first tries to open the lower file directly with `O_RDONLY` for read-only lower inodes or `O_RDWR` otherwise. If an `O_RDWR` direct open fails, it queues a request to the eCryptfs kernel thread, waits for completion, and returns the resulting lower file or error.

The kthread is freezable and exits when the zombie flag is set. Pending requests are completed during teardown so callers do not sleep indefinitely.

## Research Notes
This file supports the one-lower-file-per-inode model in `main.c`. Its key invariant is completion of every queued request, including during shutdown.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/kthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/main.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/main.c

## Summary
Implements eCryptfs module setup, mount parsing/validation, filesystem registration, superblock creation/destruction, lower-file reference management, sysfs version reporting, and kmem-cache lifecycle.

## Main Responsibilities
- Define module parameters for verbosity, message buffer length, message wait timeout, and estimated user count.
- Open and refcount shared lower files for upper regular inodes.
- Parse fs_context mount parameters for signatures, ciphers, key sizes, passthrough, xattr metadata, encrypted view, filename encryption, and auth-token policy.
- Validate required mount options, cipher support, cached transforms, and registered auth tokens.
- Reject unsupported mount situations: missing source, recursive eCryptfs mount, idmapped lower mount, failed owner check, excessive stack depth, and FIPS mode.
- Build the eCryptfs superblock over a lower directory and mirror lower superblock limits/flags.
- Initialize and destroy module kmem caches.
- Register `/sys/fs/ecryptfs/version`.
- Initialize and tear down kthread, messaging, crypto, and filesystem registration.

## Key APIs
- `ecryptfs_get_lower_file()`
- `ecryptfs_put_lower_file()`
- `ecryptfs_parse_param()`
- `ecryptfs_validate_options()`
- `ecryptfs_get_tree()`
- `ecryptfs_init()` / `ecryptfs_exit()`

## Important Behavior
A regular upper inode keeps at most one lower file open. The first caller opens it through `ecryptfs_init_lower_file()`, increments are counted atomically, and the final put writes back the upper mapping before `fput()`.

Mount validation requires at least one auth-token signature and verifies cipher support by creating or finding cached transforms. Filename encryption defaults to the content cipher and key size unless filename-specific options are supplied.

Encrypted-view mounts force xattr metadata and make the eCryptfs mount read-only. Lower read-only mounts also force the upper mount read-only.

## Research Notes
This file is the module lifecycle and mount-policy entry point. It coordinates most other files: caches for all private objects, kthread lower opens, messaging for ecryptfsd, crypto transform cache initialization, and VFS registration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/messaging.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/messaging.c

## Summary
Implements the in-kernel messaging core used to communicate with per-user ecryptfsd daemons through the miscdevice layer. It manages daemon registration lookup, fixed message-context pools, request sequencing, response delivery, wait/timeout behavior, and messaging teardown.

## Main Responsibilities
- Maintain free and allocated lists of `ecryptfs_msg_ctx` objects.
- Maintain a hash table of ecryptfsd daemon objects keyed by current effective UID.
- Allocate a free message context for outbound requests and assign monotonically increasing counters.
- Queue outbound messages to the matching daemon through `ecryptfs_send_miscdev()`.
- Process userspace responses by validating context index, pending state, and sequence counter.
- Wake the sleeping requester when a response arrives.
- Wait for responses with `ecryptfs_message_wait_timeout`.
- Initialize and release message context arrays, daemon hash buckets, and the miscdevice layer.
- Destroy live daemon objects and pending messages during teardown.

## Key APIs
- `ecryptfs_spawn_daemon()`
- `ecryptfs_exorcise_daemon()`
- `ecryptfs_find_daemon_by_euid()`
- `ecryptfs_send_message()`
- `ecryptfs_wait_for_response()`
- `ecryptfs_process_response()`
- `ecryptfs_init_messaging()`
- `ecryptfs_release_messaging()`

## Important Behavior
Each outbound request reserves a context from a fixed-size pool. Responses must reference a valid context index and match the current sequence counter, preventing stale or misrouted userspace replies from completing the wrong request.

Daemon lookup is by effective UID. If no daemon exists for the current euid, sending returns `-ENOTCONN`. If no context is free, sending fails with `-ENOMEM` and recommends increasing `ecryptfs_message_buf_len`.

`ecryptfs_wait_for_response()` uses interruptible timeout sleeps and always moves the context back to the free list before returning. Successful callers receive ownership of the copied response message.

## Research Notes
This file backs public-key FEK encryption/decryption paths in `keystore.c`. Its main invariants are list locking order, context state transitions, daemon hash locking, sequence matching, and cleaning queued messages when daemons disappear.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/messaging.c -->