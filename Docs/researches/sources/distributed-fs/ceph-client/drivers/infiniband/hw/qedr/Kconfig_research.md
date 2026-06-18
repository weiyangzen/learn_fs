# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Kconfig

## Purpose
`Kconfig` defines the build-time configuration symbol for the QLogic/FastLinQ QEDR RDMA driver. It lets kernel configuration select the low-level InfiniBand-over-Ethernet support for QED host channel adapters.

## Important APIs, Types, And Functions
The relevant symbol is `INFINIBAND_QEDR`, a tristate named "QLogic RoCE driver". It depends on `64BIT`, `QEDE`, and `PCI`, and selects `QED_LL2`, `QED_OOO`, and `QED_RDMA`.

## Control Flow
There is no runtime control flow. At configuration time, enabling this symbol causes the build system to compile the QEDR module or link it built-in according to tristate selection. The selected QED feature symbols ensure the lower-layer Ethernet/RDMA and LL2 interfaces used by `main.c`, `qedr_roce_cm.c`, and `qedr_iw_cm.c` are available.

## State And Persistence Behavior
The only state is kernel configuration state in `.config`. It persists across builds through normal kernel config mechanisms and controls whether `qedr.o` is built.

## Dependencies And Integration Points
The dependencies encode that QEDR is a PCI, 64-bit-only RDMA client layered on the `qede`/`qed` networking stack. The selected symbols match the driver's use of QED RDMA operations, LL2 packet paths for RoCE GSI, and out-of-order support.

## Risks And Test Signals
Risk is mostly configuration skew: missing selects would surface as unresolved QED symbols, while overly broad dependencies would offer the driver where the lower layer cannot provide RDMA services. Test signals include `olddefconfig` visibility checks, module build with `CONFIG_INFINIBAND_QEDR=m`, built-in build with `=y`, and dependency builds where `QEDE` or `PCI` are disabled.
