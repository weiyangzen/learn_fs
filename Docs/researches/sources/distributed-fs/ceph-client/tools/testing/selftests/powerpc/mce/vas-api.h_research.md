<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/vas-api.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/vas-api.h

Purpose: Local copy of the userspace VAS ioctl ABI needed by the MCE test. It defines how to request a transmit window from `/dev/crypto/nx-gzip`.

Important APIs and types: Defines `VAS_MAGIC`, `VAS_TX_WIN_OPEN`, `VAS_TX_WIN_FLAG_QOS_CREDIT`, and `struct vas_tx_win_open_attr` with version, VAS id, reserved fields, and flags.

Control flow: No executable control flow. Callers fill `vas_tx_win_open_attr` and pass it to `ioctl(fd, VAS_TX_WIN_OPEN, ...)`.

State and persistence: No mutable state. The structure describes kernel-created VAS state after ioctl success.

Dependencies and integration points: Depends on `<linux/types.h>` and `<asm/ioctl.h>`. Duplicated in the NX gzip include tree for standalone build locality.

Risks: ABI drift from the kernel UAPI header would cause ioctl failures or incorrect window attributes. Reserved fields should remain zeroed by callers.

Test signals: Compile success plus successful VAS_TX_WIN_OPEN calls in MCE/NX tests validate this header copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/vas-api.h -->
