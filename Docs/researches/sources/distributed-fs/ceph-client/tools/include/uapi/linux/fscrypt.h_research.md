# sources/distributed-fs/ceph-client/tools/include/uapi/linux/fscrypt.h

Purpose: defines the userspace ioctl ABI for filesystem encryption policies and key management on fscrypt-capable filesystems. It supports legacy v1 policies and recommended v2 policies with HKDF and key verification.

Important APIs/types: policy flags cover filename padding, direct keys, and IV inode/logical-block modes. Encryption modes include AES-XTS/CTS/CBC, SM4, Adiantum, and AES-HCTR2. Types include `fscrypt_policy_v1`, legacy `fscrypt_key`, `fscrypt_policy_v2`, `fscrypt_get_policy_ex_arg`, `fscrypt_key_specifier`, `fscrypt_provisioning_key_payload`, `fscrypt_add_key_arg`, `fscrypt_remove_key_arg`, and `fscrypt_get_key_status_arg`. Ioctls include `FS_IOC_SET/GET_ENCRYPTION_POLICY`, `FS_IOC_GET_ENCRYPTION_POLICY_EX`, add/remove key, get key status, and get nonce.

Control flow, state, and persistence: userspace sets an encryption policy on an empty directory, provisions keys by descriptor or identifier, checks/removes keys, and then file creation/open paths enforce encryption. Persistent state is on-disk policy metadata and per-filesystem key availability; raw keys are transient and should not be persisted by this ABI.

Dependencies and integration points: depends on ioctl and types headers and is included by `fs.h` for non-kernel users. It integrates ext4/f2fs/ubifs encryption, Linux keyrings, hardware-wrapped keys, and provisioning services.

Risks and test signals: risks include using deprecated v1 descriptors, leaking raw keys, unsupported mode/flag combinations, nonzero reserved fields, and removal while files remain busy. Tests should set/get v1 and v2 policies, add/remove keys for all specifier types, verify status flags, reject invalid reserved fields, and perform encrypted file I/O across mount/remount.
