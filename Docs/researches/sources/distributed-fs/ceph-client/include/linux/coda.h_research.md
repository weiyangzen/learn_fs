# sources/distributed-fs/ceph-client/include/linux/coda.h

Purpose: This kernel header bridges the Coda distributed filesystem definitions by setting up a legacy `u_quad_t` typedef and including the UAPI Coda header.

Important APIs/types/functions: It defines include guard `_CODA_HEADER_`, typedefs `u_quad_t` as `unsigned long long`, and includes `<uapi/linux/coda.h>`.

Control flow: There is no runtime control flow; inclusion exposes UAPI Coda structures and constants to kernel code.

State and persistence behavior: It owns no state. The persistent contract is the Coda kernel/userspace ABI included from UAPI.

Dependencies and integration points: It integrates Coda filesystem kernel code with UAPI request/response structures shared with userspace Venus/Coda tools.

Risks: The typedef is legacy compatibility glue; changing it can break ABI assumptions. Most substantive structure changes must happen in the UAPI header with compatibility care.

Test signals: Coda filesystem build coverage, mount/client smoke tests, ioctl/message ABI tests, and userspace Coda tool compatibility validate behavior.
