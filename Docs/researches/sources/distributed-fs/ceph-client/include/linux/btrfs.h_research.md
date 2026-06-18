## sources/distributed-fs/ceph-client/include/linux/btrfs.h

**Purpose:** This kernel header is a thin include wrapper that exposes Btrfs UAPI definitions to in-kernel users through `linux/btrfs.h`.

**Important APIs/types/functions:** It declares no new symbols. Its only functional content is `#include <uapi/linux/btrfs.h>`.

**Control flow, state, persistence:** There is no control flow or runtime state. Persistence semantics are entirely in the Btrfs filesystem and UAPI structures/constants included from the UAPI header.

**Dependencies/integration:** Integrates kernel code with Btrfs ioctl/format constants while preserving the conventional `linux/` include path.

**Risks and test signals:** Risks are mostly include-order or accidental divergence from UAPI. Test signals are successful builds of in-kernel Btrfs consumers and ABI tests that include the UAPI header through both paths.
