# sources/distributed-fs/ceph-client/include/uapi/linux/loadpin.h

Purpose: defines the LoadPin userspace ioctl used to configure trusted dm-verity root digests through securityfs.

Important APIs and types: `LOADPIN_IOC_MAGIC` and `LOADPIN_IOC_SET_TRUSTED_VERITY_DIGESTS` are the only exported ABI items. The ioctl takes an unsigned-int-sized fd argument identifying a file containing ASCII root digests.

Control flow: userspace writes or prepares a digest list file, opens the LoadPin securityfs control node `loadpin/dm-verity`, and calls the ioctl with the digest-list fd. The kernel reads and installs trusted verity digests used by LoadPin policy.

State and persistence: trusted digest configuration is kernel security-module state and may affect subsequent file-loading decisions. The header itself stores nothing; persistence across boot/update depends on userspace reconfiguration.

Dependencies and integration points: depends on ioctl numbering and securityfs exposure from LoadPin. Integrates dm-verity, LoadPin LSM policy, and boot/update trust provisioning tools.

Risks and test signals: risks include wrong ioctl target, malformed digest files, fd lifetime/permission mistakes, and failure to reject unsupported formats. Test securityfs ioctl success/failure, valid and invalid digest lists, repeated configuration, and enforcement against trusted/untrusted verity-backed loads.
