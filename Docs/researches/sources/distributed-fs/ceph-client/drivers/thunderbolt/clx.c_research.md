# sources/distributed-fs/ceph-client/drivers/thunderbolt/clx.c

## Purpose
`clx.c` manages Thunderbolt/USB4 CLx low-power states on high-speed lanes, including detection, enable/disable, PM secondary resolution, and Titan Ridge objection masking.

## Important APIs, Types, and Functions
Public APIs are `tb_port_clx_is_enabled`, `tb_switch_clx_init`, `tb_switch_clx_enable`, and `tb_switch_clx_disable`. The module parameter `clx` controls global enablement. Internal helpers read/write lane adapter CL bits, check support, resolve primary/secondary PM roles, validate masks, and mask objections.

## Control Flow
Initialization skips ICM/host routers and unsupported/quirked platforms, then reads upstream and downstream CLx state and stores it in `sw->clx`. Enable validates requested state ordering, requires supported parent/child routers, restricts CL2 to USB4 v2 routers, resolves PM secondary roles, checks both link ends, enables requested CL bits on both ports, masks Titan Ridge objections, and rolls back on failure. Disable clears all stored CL states on both link ends unless the switch is unplugged, in which case it returns the remembered state without touching hardware.

## State and Persistence Behavior
`sw->clx` records enabled CL states for each switch. Hardware lane adapter control bits and Titan Ridge low-power objection masks are modified. The `clx_enabled` module parameter is read-only after module load.

## Dependencies and Integration Points
It depends on Thunderbolt port/switch config reads/writes, USB4 CLx support helpers, link-controller support checks, router generation predicates, quirks, lane adapter registers, and low-power capability offsets.

## Risks and Edge Cases
CLx is disabled for dual single-lane links, xdomain links, Tiger Lake, quirked routers, and unsupported endpoints. Partial enable failures must roll back both sides. CL1 requires CL0s in the validation mask, and CL2 requires v2 routers.

## Test Signals
Mocked switch/port tests for support filtering, mask validation, CL2 version gating, upstream/downstream mismatch warnings, enable rollback, Titan Ridge objection programming, unplugged disable behavior, and module parameter disabled mode.
