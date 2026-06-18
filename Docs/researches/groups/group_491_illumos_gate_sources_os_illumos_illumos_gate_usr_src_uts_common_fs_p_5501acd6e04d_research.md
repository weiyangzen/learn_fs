# Group Research: group_491_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_p_5501acd6e04d

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvnops.c

## Purpose

`prvnops.c` is the illumos procfs vnode operation implementation. It maps VFS calls on `/proc`, `/proc/self`, `/proc/<pid>`, process files, LWP files, fd/object/path/contract directories, and old procfs compatibility files onto live kernel process, thread, address-space, file-descriptor, credential, contract, and control state.

The exported operation table is `pr_vnodeops_template`. The file is both namespace construction logic for procfs and the read/write/access layer for process observability and control.

## Main Interfaces

Important VOP entry points are `propen`, `prclose`, `prread`, `prwrite`, `prioctl`, `prgetattr`, `praccess`, `prlookup`, `prcreate`, `prreaddir`, `prreadlink`, `prinactive`, `prcmp`, `prrealvp`, and `prpoll`.

The file dispatches reads through `pr_read_function[]` and, when `_SYSCALL32_IMPL` is present, `pr_read_function_32[]`. It dispatches directory lookup and readdir through `pr_lookup_function[]` and `pr_readdir_function[]`.

Major helpers include `prgetnode`, `prfreenode`, `prfreecommon`, `prlwpnode`, `rebuild_objdir`, `obj_entry`, `pr_list_unlink`, `prreadlink_lookup`, and many per-file read routines such as `pr_read_status`, `pr_read_lstatus`, `pr_read_psinfo`, `pr_read_map_common`, `pr_read_fdinfo`, `pr_read_priv`, `pr_read_xregs`, and their 32-bit variants.

## Behavior And Data Flow

Opening procfs files validates the target process with `pr_p_lock()` or `prlock()`, tracks writer and self-writer counts in `prcommon_t`, enforces exclusive procfs writer semantics, and performs file-specific setup such as `hat_startstat()` for pagedata files. Closing reverses these counts, frees page-stat state, notifies waiters, and runs last-close behavior such as cancelling watchpoints, clearing trace masks, applying run-on-last-close, or killing the target process.

Reads are structured snapshots of live kernel state. Process and LWP status, psinfo, usage, credentials, privileges, secflags, sigactions, auxv, memory maps, watchpoints, xregs, SPARC register windows, file-descriptor info, and old procfs address-space reads all follow type-specific locking rules. Many routines allocate result buffers outside or around `p_lock` to avoid sleeping while holding process locks.

Writes are limited to address-space/process pseudo-files, control files, and `lwpname`. Control writes are delegated to `prwritectl()` or `prwritectl32()`. Address-space writes use `prusrio()`. LWP name writes require a complete bounded NUL-terminated printable string.

`prgetattr()` manufactures vnode attributes for procfs pseudo-files, with special handling for underlying object/fd/current-root vnodes, dynamic directory sizes, 32-bit caller structure sizes, address-space map sizes, fdinfo size calculation, pagedata sizing, contract links, and architecture-specific files.

## Namespace Model

`prlookup()` routes directory lookups by procfs node type. `/proc` numeric entries create or reuse process directory vnodes after PID visibility and `secpolicy_basic_procinfo()` checks. `/proc/<pid>` static entries come from `piddir[]`; `/proc/<pid>/lwp/<lwpid>` entries come from `lwpiddir[]`; fd/fdinfo/path/object/contract/template directories are generated dynamically from the target process.

`pr_readdir_*()` functions emit matching directory contents. Top-level `/proc` walks the proc table filtered by zone and policy. Object/path directories rebuild or consult address-space object directories. fd/fdinfo directories walk `uf_info_t`. LWP directories walk `p_lwpdir`. Contract directories use `contract_plookup()`.

The file supports procfs "wormholes" for `fd`, `cwd`, `root`, and object nodes by storing `pr_realvp` and sometimes returning or traversing underlying filesystem vnodes. `VTRAVERSE` is deliberately required for these cases to avoid misleading VFS path-name caching.

## Locking And Lifetime

The implementation depends on a specific lock order around `pr_pidlock`, `pidlock`, `p_lock`, address-space locks, file-table locks, `pr_mutex`, `prc_mutex`, and poll locks. It repeatedly drops `p_lock` before operations that may sleep, perform I/O, touch user memory, grab address-space locks, or call into VFS.

`prgetnode()` allocates procfs vnodes and initializes type-specific mode, vnode type, file arrays, old-proc compatibility nodes, and common state. `prinactive()` unlinks vnodes from process/LWP lists, clears parent file arrays, releases underlying vnodes and contracts, and frees `prnode_t`/`prcommon_t` state when references reach zero.

## Security And Compatibility

`praccess()` enforces readonly mounts, owner/root semantics, process credential permission checks, executable readability checks for sensitive files, fd open-mode limitations, and special world-readable files such as `psinfo`, `lpsinfo`, `lwpsinfo`, and usage files.

The file has extensive compatibility behavior: old process and LWP pseudo-files, old pagedata reads, 32-bit structure exports, `EOVERFLOW` for 32-bit callers inspecting 64-bit targets, `PR_OFFMAX`, old directory write compatibility, x86 LDT support, and SPARC-only register files.

## Dependencies

This file depends on procfs internals in `fs/proc/prdata.h`, process and LWP state in `sys/proc.h`, procfs control code in `prioctl.c`, VM/address-space interfaces, HAT pagedata statistics, generic filesystem helpers, contract APIs, VFS/vnode APIs, credential and privilege policy helpers, polling, and architecture-specific register support.

## Research Notes

This is a high-risk procfs boundary file because it exposes live kernel process state through VFS while racing process exit, exec, LWP creation/destruction, file-table changes, address-space mutation, poll notification, and zone visibility. Important audit areas are lock dropping around process lifetime, `pr_realvp` traversal behavior, old-proc compatibility paths, 32-bit conversion sizes, fd/path object lookup races, last-close side effects, and signature-sensitive return codes such as `ENOENT`, `EAGAIN`, `EBUSY`, `EOVERFLOW`, and `EBADRPC`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vfsops.c

## Purpose

`sharefs_vfsops.c` implements the VFS/module side of the kernel `sharefs` pseudo filesystem. `sharefs` exposes the in-kernel share table as a read-only pseudo-file, traditionally mounted as `sharetab`.

## Main Interfaces

The file defines module entry points `_init`, `_info`, and `_fini`, registers the `sharefs` filesystem and `sharefs` syscall, initializes vnode and VFS operation vectors, and exports `sharefs_ops_data`.

The VFS operation table `sharefs_vfstops[]` installs `sharefs_mount`, `sharefs_unmount`, `sharefs_root`, and `sharefs_statvfs`.

## Behavior And Data Flow

`sharefs_init()` records the filesystem type, installs VFS ops with `vfs_setfsops()`, creates GFS vnode operation vectors with `gfs_make_opsvec()`, allocates a pseudo-device major, and initializes per-zone sharetab state through `sharefs_sharetab_init()`.

`sharefs_mount()` requires mount privilege, rejects non-overlay busy mountpoints, allocates `sharefs_vfs_t`, assigns a unique pseudo-device/minor pair, fills `vfs_bsize`, `vfs_fstype`, `vfs_fsid`, `vfs_data`, and `vfs_dev`, then creates the root pseudo-file via `sharefs_create_root_file()`.

`sharefs_unmount()` requires unmount privilege, rejects forced unmounts, checks that no active vnodes hold the root beyond the mount reference, releases the root vnode, and frees the per-mount data. `sharefs_root()` returns the root vnode with a hold. `sharefs_statvfs()` returns a one-file, read-only pseudo-filesystem view.

## Dependencies

This file depends on GFS pseudo-file helpers, `sharefs/sharefs.h`, VFS registration, module/syscall registration, mount policy checks, pseudo-device allocation, and `sharefs_vnops.c` for root-file construction.

## Research Notes

The filesystem is intentionally non-unloadable: `_fini()` always returns `EBUSY`. The notable correctness points are per-mount pseudo-device uniqueness, root vnode reference accounting during unmount, and the relationship between VFS initialization and per-zone sharetab initialization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vnops.c

## Purpose

`sharefs_vnops.c` implements the vnode operations for the `sharefs` pseudo-file that presents the kernel share table as read-only text. It creates per-open snapshots so readers see stable sharetab contents while the underlying in-kernel share list may change.

## Main Interfaces

The vnode operation table `sharefs_tops_data[]` installs `sharefs_open`, `sharefs_close`, `sharefs_getattr`, `sharefs_access`, `sharefs_inactive`, `sharefs_read`, and `fs_seek`, with ioctl rejected by `fs_inval`.

Other important routines are `sharefs_snap_create()` and `sharefs_create_root_file()`.

## Behavior And Data Flow

`sharefs_create_root_file()` creates the mounted root pseudo-file with `gfs_root_create_file()` and marks it as the real sharetab vnode. `sharefs_open()` rejects write opens, creates a fresh GFS vnode for the open instance, holds the parent VFS, marks the vnode as uncached/unmappable/root-like pseudo data, releases the original vnode, and builds a snapshot.

`sharefs_snap_create()` locks `sharefs_lock` as writer and `sharetab_lock` as reader. If an existing snapshot matches `sharetab_generation`, it reuses it. Otherwise it frees stale snapshot memory, copies `sharetab_size` and `sharetab_count`, allocates a NUL-terminated buffer, walks each filesystem share table and hash bucket, formats entries as tab-separated `path res fstype opts descr` lines, records snapshot time and generation, and validates count/size accounting.

`sharefs_read()` refreshes the snapshot when reading from offset zero, bounds the requested read against `sharefs_size`, rejects negative offsets or impossible lengths, and copies from the snapshot with `uiomove()`.

`sharefs_getattr()` returns regular read-only file attributes. For the root/real vnode it reports current global sharetab size and mtime; for opened snapshot vnodes it reports snapshot size and time. `sharefs_close()` and `sharefs_inactive()` release snapshot buffers when the open instance is no longer used.

## Dependencies

The vnode code depends on sharetab globals and locks from `sharetab.c`, GFS file/root creation, `uiomove()`, vnode/VFS reference management, and `sharefs/sharefs.h` structures such as `shnode_t`, `sharetab_globals_t`, `sharetab_t`, and `share_t`.

## Research Notes

The central invariant is that text exported to userspace comes from a stable per-open snapshot, not from live sharetab entries while they can be replaced or removed. Audit points are size accounting in `sharefs_snap_create()`, generation reuse, lock ordering between `sharefs_lock` and `sharetab_lock`, and cleanup on open/read/inactive error paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharefs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharetab.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharetab.c

## Purpose

`sharetab.c` maintains the per-zone in-kernel share table behind `sharefs` and implements the `sharefs` syscall operations for adding, replacing, and removing share records.

## Main Interfaces

Public entry points are `sharefs_sharetab_init()`, `sharetab_get_globals()`, `sharefs_impl()`, and `sharefs()`. Internal helpers include `sharefree()`, `sharefs_add()`, `sharefs_remove()`, `sharetab_zone_init()`, and `sharetab_zone_fini()`.

The syscall accepts `enum sharefs_sys_op` values such as `SHAREFS_ADD`, `SHAREFS_REPLACE`, and `SHAREFS_REMOVE` plus a user `share_t` with string fields.

## Behavior And Data Flow

Per-zone state is allocated by `sharetab_zone_init()` and attached with `zone_key_create()`. Each zone gets `sharetab_lock`, `sharefs_lock`, share count, aggregate text size, generation number, mtime, snap time, and a linked list of per-filesystem share hash tables.

`sharefs_impl()` first checks whether remove/replace can possibly succeed, copies in the user `share_t`, allocates a temporary copy buffer sized by `iMaxLen`, copies mandatory `path` and `fstype` strings, then copies `res`, `opts`, and `descr` for add/replace. The `SHARETAB_COPYIN` macro allocates kernel strings, records lengths in `sharefs_lens_t`, and contributes to `sh_size`.

`sharefs_add()` finds or creates the per-fstype share table, computes the hash bucket from path, computes exported text size including separators and newline, replaces an existing exact path match or inserts a new share at the bucket head, updates bucket/table/global counts, updates aggregate size, mtime, and generation, and frees replaced entries.

`sharefs_remove()` finds the matching fstype and exact path entry, unlinks it from the hash bucket, decrements counts, subtracts size, updates mtime and generation, frees both the stored share and the caller's temporary share, and returns `ENOENT` when no match exists.

`sharetab_zone_fini()` destroys locks and walks every fstype table and bucket, freeing all shares, fstype strings, table nodes, and the per-zone globals.

## Security And Zones

`sharefs()` enforces privileges before calling `sharefs_impl()`: global-zone callers require `secpolicy_sys_config()`, while non-global zones use `secpolicy_nfs()` to match existing ZFS share policy behavior. All state lookup uses `sharetab_get_globals(curzone)` or the mount zone.

## Dependencies

The file depends on zone-specific storage, kernel memory allocation, `copyin()`/`copyinstr()`, policy checks, atomic counters, high-resolution timestamps, the `pkp_tab_hash()` hash function, and sharefs structures from `sharefs/sharefs.h`.

## Research Notes

This file is the mutation side of the sharefs snapshot model. Important audit points are trusting `iMaxLen` for copy buffer sizing, path-length comparisons that mix copied length and `strlen()`, `sharetab_size` accounting used by `sharefs_snap_create()`, generation increments, and privilege behavior in non-global zones.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sharefs/sharetab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb.conf -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb.conf

## Purpose

`nsmb.conf` is the driver configuration file for the illumos SMB client kernel module.

## Contents

After the CDDL header and copyright block, it declares:

```text
name="nsmb" parent="pseudo";
```

This attaches the `nsmb` device as a pseudo device rather than a hardware-enumerated device.

## Dependencies

The file is consumed by illumos driver/module configuration tooling and corresponds to the `nsmb` SMB client pseudo-device.

## Research Notes

There is no executable logic here. The main operational effect is module attachment under the `pseudo` parent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_crypt_kcf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_crypt_kcf.c

## Purpose

`nsmb_crypt_kcf.c` provides kernel-side SMB3 encryption and decryption helpers backed by the Kernel Cryptographic Framework. It intentionally keeps SMB-specific knowledge limited to constants and structures from `nsmb_kcrypt.h`.

## Main Interfaces

The file exports `nsmb_aes_ccm_getmech()`, `nsmb_aes_gcm_getmech()`, `nsmb_crypto_init_ccm_param()`, `nsmb_crypto_init_gcm_param()`, `nsmb_encrypt_init()`, `nsmb_decrypt_init()`, `nsmb_enc_ctx_done()`, `nsmb_encrypt_mblks()`, and `nsmb_decrypt_mblks()`.

## Behavior And Data Flow

`find_mech()` maps mechanism names such as `SUN_CKM_AES_CCM` and `SUN_CKM_AES_GCM` to KCF mechanism IDs. The CCM and GCM parameter initializers populate KCF parameter structures with nonce, authenticated data, tag/MAC size, and data size where required.

`nsmb_encrypt_init()` and `nsmb_decrypt_init()` stash a raw key in `crypto_key_t`, with key length converted to bits. There is no KCF context setup until whole-message encrypt/decrypt calls.

`nsmb_encrypt_mblks()` encrypts an mblk chain in place using `crypto_encrypt()`. It treats input length as cleartext length and output length as cleartext plus the 16-byte SMB2 signature/tag size. `nsmb_decrypt_mblks()` rejects ciphertext shorter than or equal to the tag size and decrypts in place, producing ciphertext length minus tag size.

## Dependencies

The file depends on KCF APIs, STREAMS mblk crypto data support, `msgsize()`, SMB crypto constants in `nsmb_kcrypt.h`, and mechanism names from illumos crypto headers.

## Research Notes

The primary correctness constraints are mblk length accounting, tag-size assumptions, nonce-size assertions, and matching KCF CCM/GCM parameters to SMB3 transform-header construction elsewhere. Failures log KCF return codes and return `-1`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_crypt_kcf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kcrypt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kcrypt.h

## Purpose

`nsmb_kcrypt.h` defines the shared SMB client crypto abstraction used by signing, preauth hashing, key derivation, and encryption code. It supports both kernel KCF and user-space PKCS#11 implementations via conditional typedefs.

## Main Interfaces

The header defines key and digest constants such as `AES128_KEY_LENGTH`, `AES256_KEY_LENGTH`, `MD5_DIGEST_LENGTH`, `SHA256_DIGEST_LENGTH`, `SHA512_DIGEST_LENGTH`, `SMB2_SIG_SIZE`, `SMB2_KEYLEN`, `SMB3_AES_CCM_NONCE_SIZE`, and `SMB3_AES_GCM_NONCE_SIZE`.

Kernel builds map `smb_crypto_mech_t` to `crypto_mechanism_t` and `smb_sign_ctx_t` to `crypto_context_t`; user builds map them to PKCS#11 types. `smb_enc_ctx_t` wraps mechanism parameters, key material or key handles, and encryption context state.

Function prototypes cover MD5, HMAC-SHA256, AES-CMAC, SHA512, one-shot HMAC, SMB3 KDF, AES-CCM/GCM parameter initialization, encrypt/decrypt initialization, mblk encrypt/decrypt, and context cleanup.

## Dependencies

Kernel compilation depends on `<sys/crypto/api.h>`; user-space compilation depends on PKCS#11 headers. Both variants include STREAMS and UIO types because the crypto helpers operate on SMB message buffers.

## Research Notes

This header is the contract between higher-level SMB2/3 protocol code and the concrete kernel/user crypto implementations. Compatibility risks come from keeping structure layouts and function semantics aligned with the parallel user-space implementation and with SMB server-side crypto abstractions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kcrypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kdf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kdf.c

## Purpose

`nsmb_kdf.c` implements the SMB3 key derivation function described by MS-SMB2 and NIST SP800-108. It derives signing, application, encryption, and decryption keys from a session key, label, and context.

## Main Interfaces

The exported function is `nsmb_kdf(uint8_t *outbuf, uint32_t keylen, uint8_t *ssn_key, size_t ssn_keylen, uint8_t *label, size_t label_len, uint8_t *context, size_t context_len)`.

## Behavior And Data Flow

The function builds the fixed SP800-108 counter-mode input:

```text
counter || label || 0x00 || context || L
```

It uses a big-endian counter value of 1 and encodes output key length `L` in bits. Labels are limited to 16 bytes and contexts to 64 bytes, matching the fixed stack buffer. The PRF is HMAC-SHA256 using the session key. The resulting SHA-256 digest is copied to `outbuf` for the requested key length.

The file documents SMB 3.0.2 labels such as `SMB2AESCMAC`, `SMB2APP`, and `SMB2AESCCM`, and SMB 3.1.1 labels such as `SMBSigningKey`, `SMBS2CCipherKey`, and `SMBC2SCipherKey`.

## Dependencies

This file depends on `nsmb_hmac_getmech()` and `nsmb_hmac_one()` from the signing crypto layer, byte-order assumptions encoded manually into the KDF buffer, and constants from `nsmb_kcrypt.h`.

## Research Notes

The function asserts and fails on oversize label/context inputs. Callers must pass a `keylen` no larger than the SHA-256 digest length; current SMB callers derive 16- or 32-byte keys. The key-length field uses only the lower 16 bits after two zero bytes, which is suitable for current SMB key sizes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_preauth.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_preauth.c

## Purpose

`nsmb_preauth.c` implements SMB 3.1.1 preauthentication integrity hashing for the SMB client.

## Main Interfaces

It exports `nsmb_preauth_init()` and `nsmb_preauth_calc()`.

## Behavior And Data Flow

`nsmb_preauth_init()` obtains the SHA512 mechanism and stores it in the virtual circuit's preauth mechanism field. Failure maps to `EAUTH`.

`nsmb_preauth_calc()` creates a SHA512 digest context, first digests the previous 64-byte preauth hash value, then digests every mblk segment of the current SMB message, and finally writes the new 64-byte hash value.

## Dependencies

The file depends on `smb_vc_t` preauth fields, mblk chains, and SHA512 helper functions from `nsmb_sign_kcf.c` or the user-space crypto equivalent declared in `nsmb_kcrypt.h`.

## Research Notes

This code is short but security-critical. It is used during SMB 3.1.1 negotiation and session setup before signing keys are derived. Failure accounting is handled by callers in `smb2_smb.c`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_preauth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_sign_kcf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_sign_kcf.c

## Purpose

`nsmb_sign_kcf.c` provides kernel-side digest and MAC helpers for SMB1 signing, SMB2 signing, SMB3 signing, one-shot KDF HMAC, and SMB 3.1.1 preauth hashing using KCF.

## Main Interfaces

The file exports MD5 helpers (`nsmb_md5_getmech`, `nsmb_md5_init`, `nsmb_md5_update`, `nsmb_md5_final`), HMAC-SHA256 helpers (`nsmb_hmac_getmech`, `nsmb_hmac_init`, `nsmb_hmac_update`, `nsmb_hmac_final`, `nsmb_hmac_one`), AES-CMAC helpers (`nsmb_cmac_getmech`, `nsmb_cmac_init`, `nsmb_cmac_update`, `nsmb_cmac_final`), and SHA512 helpers (`nsmb_sha512_getmech`, `nsmb_sha512_init`, `nsmb_sha512_update`, `nsmb_sha512_final`).

## Behavior And Data Flow

`find_mech()` maps KCF mechanism names to IDs and logs missing mechanisms. MD5 and SHA512 use `crypto_digest_*` APIs. HMAC-SHA256 and AES-CMAC use `crypto_mac_*` APIs with raw keys measured in bits.

`nsmb_hmac_final()` computes the full SHA-256 HMAC but copies only the first 16 bytes to the caller because SMB2 signatures use a truncated HMAC. `nsmb_cmac_final()` emits the 16-byte AES-CMAC directly. `nsmb_hmac_one()` performs a one-shot MAC and is used by the SMB3 KDF.

Update failures call `crypto_cancel_ctx()` before returning `-1`.

## Dependencies

The file depends on KCF, SMB crypto constants and typedefs from `nsmb_kcrypt.h`, kernel memory/common error headers, and mechanism names such as `SUN_CKM_MD5`, `SUN_CKM_SHA256_HMAC`, `SUN_CKM_AES_CMAC`, and `SUN_CKM_SHA512`.

## Research Notes

This is the low-level signing primitive layer. Higher-level protocol code is responsible for zeroing SMB2 signature fields before MAC calculation and for choosing HMAC vs CMAC. Audit points are context cancellation on error, truncation semantics for SMB2 HMAC, and consistency with the user-space PKCS#11 implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_sign_kcf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/offsets.in -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/offsets.in

## Purpose

`offsets.in` is input for `ctfstabs`, used to generate `ioc_check.h` so SMB client ioctl data structures can be checked for 32-bit and 64-bit ABI layout invariance.

## Contents

The file includes kernel and SMB client headers, then lists structures and selected members whose offsets or sizes must be tracked. Covered structures include `smbioc_sockaddr`, `smbioc_ssn_ident`, `smbioc_ossn`, `smbioc_oshare`, `smbioc_tcon`, `smbioc_ssn_work`, `smbioc_rw`, `smbioc_xnp`, `smbioc_ntcreate`, `smbioc_printjob`, and `smbioc_pk`.

Several entries request generated size or field constants such as `SIZEOF_SMBIOC_RW`, `SIZEOF_SMBIOC_XNP`, `SIZEOF_NTCREATE`, `IOC_NTCR_NAME`, `SIZEOF_PRINTJOB`, and `SIZEOF_SMBIOC_PK`.

## Dependencies

The generated output depends on definitions from `<netsmb/smb.h>`, `<netsmb/netbios.h>`, `<netsmb/smb_dev.h>`, and system type/DDI/socket headers.

## Research Notes

This file is ABI guard metadata, not runtime logic. Changes to SMB ioctl structures should update or validate this list so 32/64-bit ioctl compatibility remains checked.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/offsets.in -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.c

## Purpose

`smb2_rq.c` implements SMB2/3 request header construction, enqueueing, waiting, reply verification, and SMB2 header parsing for the SMB client.

## Main Interfaces

Exported functions are `smb2_rq_fillhdr()`, `smb2_rq_simple()`, `smb2_rq_simple_timed()`, `smb2_rq_internal()`, and `smb2_rq_parsehdr()`. Internal helpers are `smb2_rq_enqueue()` and `smb2_rq_reply()`.

## Behavior And Data Flow

`smb2_rq_fillhdr()` rewinds a duplicate of the first request mblk and writes the 64-byte SMB2 header: protocol signature, structure size, credit charge/request, status placeholder, command, flags, next-command offset, message ID, process ID, tree ID, and session ID. The signature field is left for signing code.

`smb2_rq_simple_timed()` prepares a request state and timeout, enqueues it, then waits for and parses the reply. `smb2_rq_enqueue()` handles reconnect and tree-connect state unless `SMBR_NORECONNECT` is set, fills request session/tree IDs, and queues through `smb2_iod_addrq()`.

`smb2_rq_internal()` is for IOD connection setup and echo-like internal requests. It bypasses reconnect/tree-connect logic, marks requests internal, waits with `smb_iod_waitrq_int()`, verifies signed non-encrypted replies, parses headers, and deliberately leaves raw NT status for callers.

`smb2_rq_reply()` waits for normal replies, verifies signatures when the request was signed and the reply is not encrypted, parses the SMB2 header, maps NT status to errno, and treats `NT_STATUS_BUFFER_OVERFLOW` as non-fatal while marking `SMBR_MOREDATA`.

`smb2_rq_parsehdr()` decodes the SMB2 header, requires structure size 64, records status, command, credits, flags, next command, message ID, process/tree or async ID, session ID, and skips the 16-byte signature.

## Dependencies

This file depends on SMB request structures, IOD queue/wait helpers, reconnect and tree-connect helpers, SMB2 signing verification, mbchain/mdchain helpers, and NT-status-to-errno mapping.

## Research Notes

The key invariants are that headers are finalized only after message ID and tree/session IDs are known, signed replies are verified before header status is trusted, internal requests do not recursively reconnect, and buffer overflow status is exposed through flags rather than returned as a hard error.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.h

## Purpose

`smb2_rq.h` declares the SMB2/3 request helper API implemented by `smb2_rq.c`.

## Main Interfaces

It declares `smb2_rq_parsehdr()`, `smb2_rq_fillhdr()`, `smb2_rq_simple()`, `smb2_rq_simple_timed()`, and `smb2_rq_internal()`.

## Dependencies

The header depends on `struct smb_rq` being visible to includers through other SMB client headers. It includes `<sys/types.h>` and documents that SMB2 structures should be padded to 8-byte boundaries.

## Research Notes

This is a narrow interface header. Its main role is separating generic SMB2 request flow from operation-specific code in files such as `smb2_smb.c`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_sign.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_sign.c

## Purpose

`smb2_sign.c` implements SMB2/3 message signing and signature verification for the SMB client. It chooses HMAC-SHA256 for SMB2.x and AES-CMAC for SMB3.x, with SMB 3.1.1 signing keys derived from the preauth hash.

## Main Interfaces

The exported functions are `smb2_sign_init()`, `smb2_rq_sign()`, and `smb2_rq_verify()`. The internal MAC engine is `smb2_compute_MAC()`, parameterized by `smb_mac_ops_t`.

## Behavior And Data Flow

`smb2_sign_init()` obtains the appropriate crypto mechanism, allocates a 16-byte MAC key, and derives it from the session key. For SMB2.x, the key is the first 16 bytes of the session key, padded or truncated. For SMB3.0/3.0.2, it uses `nsmb_kdf()` with label `SMB2AESCMAC` and context `SmbSign`. For SMB3.1.1, it uses label `SMBSigningKey` and the current preauth hash as context.

`smb2_compute_MAC()` copies the SMB2 header, zeroes the 16-byte signature field at offset 48, MACs that modified header, MACs the remainder of the first mblk, then MACs all following mblks. The final signature is written to the caller-provided buffer.

`smb2_rq_sign()` writes the computed signature directly into the request header. On crypto failure it zeros the signature field. `smb2_rq_verify()` computes the expected signature for a reply and compares it to the on-wire signature, returning `EBADRPC` on mismatch.

## Dependencies

The file depends on crypto helper functions from `nsmb_kcrypt.h`, SMB virtual circuit session/signing fields, SMB2 header layout constants, mblk chains, SMB request structures, and dialect macros.

## Research Notes

Security-sensitive details include zeroing exactly the signature field before MAC calculation, using the correct signing algorithm by dialect, refusing to proceed on MAC computation failure, and deriving SMB3.1.1 keys only after valid preauth hashing. The compare uses `bcmp()`, so this is not constant-time.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_sign.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_smb.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_smb.c

## Purpose

`smb2_smb.c` implements the main SMB2/3 protocol operations used by the illumos SMB client: negotiate, session setup, logoff, tree connect/disconnect, create/open, close, ioctl, read, write, and echo.

## Main Interfaces

Exported operations include `smb2_parse_smb1nego_resp()`, `smb2_smb_negotiate()`, `smb2_smb_ssnsetup()`, `smb2_smb_logoff()`, `smb2_smb_treeconnect()`, `smb2_smb_treedisconnect()`, `smb2_smb_ntcreate()`, `smb2_smb_close()`, `smb2_smb_ioctl()`, `smb2_smb_read()`, `smb2_smb_write()`, and `smb2_smb_echo()`.

The file also defines the supported dialect list, client capabilities, session-setup credit request count, and tunable timeouts for default, logon, open, read, write, append, and notice operations.

## Negotiation And Session Setup

`smb2_parse_smb1nego_resp()` handles the transitional SMB1 negotiate request that receives an SMB2 response, validates dialect `SMB2_DIALECT_02ff`, maps it back to the internal SMB1 marker, and adjusts SMB2 message ID state.

`smb2_smb_negotiate()` builds the SMB2 negotiate request, advertises dialects up to `vc_maxver`, optionally emits SMB 3.1.1 negotiate contexts, and parses server security mode, dialect, GUID, capabilities, max transact/read/write, security blob, and negotiate contexts. It initializes preauth hashing for SMB3.1.1, updates the preauth hash after the negotiate response, selects default AES-CCM for SMB3.0/3.0.2, initializes encryption mechanisms when possible, decides whether signing is required, backfills legacy SMB1 capability fields, validates minimum buffer sizes, and stores read/write/transaction maxima.

`smb2_smb_ssnsetup()` sends authentication blobs between kernel and user-space authentication state. It asks for credits, saves the session ID after the first response, handles `NT_STATUS_MORE_PROCESSING_REQUIRED` as `EINPROGRESS`, updates the SMB3.1.1 preauth hash during multi-step authentication, enables signing once SMB3.1.1 authentication completes, copies response security blobs to user memory, records final session flags, and rejects servers requiring encryption when the client failed to enable it.

## Tree And File Operations

`smb2_smb_treeconnect()` builds a UNC path, sends a VC-level tree connect, parses share type, share flags, share capabilities, max access, verifies required encryption support, maps SMB2 share type/capabilities to legacy share fields, and marks the share connected with the returned tree ID.

`smb2_smb_treedisconnect()` sends a short non-reconnecting disconnect with no-interrupt send semantics and clears the tree ID regardless of result. `smb2_smb_logoff()` sends a short non-reconnecting logoff when a session exists.

`smb2_smb_ntcreate()` builds an SMB2 CREATE request, skips a leading backslash in names for SMB2 semantics, optionally sends create contexts, pads the empty-variable-data case to the documented structure size, uses no-interrupt receive to avoid leaking opened FIDs, parses create action, timestamps, allocation size, EOF, attributes, file ID, and optional returned create contexts.

`smb2_smb_close()` sends a CLOSE for a persistent/volatile SMB2 file ID and uses no-interrupt send plus no reconnect to avoid racing teardown.

## Data And Control I/O

`smb2_smb_ioctl()` sends FSCTL-style SMB2 IOCTLs with optional input mblk data, receives output offset/length, always updates the caller's output size, and can return the output as an mdchain backed by an mblk.

`smb2_smb_read()` sends SMB2 READ using the uio offset and requested length, validates response structure and data offset, clamps an overlarge server-reported data length to the requested length, and moves data into the caller's `uio`.

`smb2_smb_write()` sends SMB2 WRITE with uio data and returns the server-reported written byte count. `smb2_smb_echo()` sends an internal no-reconnect ECHO request for the IOD path.

## Dependencies

This file depends on `smb2_rq.c` request helpers, mbchain/mdchain encoding and decoding, SMB IOD behavior, SMB session/share structures, negotiate-context helpers, preauth hashing, KDF/signing/encryption initialization, NT status constants, Unicode path encoding helpers, and common SMB1-compatible fields still used by shared client code.

## Research Notes

This is the operation-level SMB2/3 protocol core. High-risk areas are offset/length validation for security blobs, negotiate contexts, create contexts, IOCTL buffers, and read data; preauth hash failure propagation; signing enablement timing; encryption-required policy checks; no-interrupt handling around operations that allocate server-side IDs; and the compatibility backfill from SMB2/3 state into legacy SMB fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_smb.c -->