
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.h

## Purpose
Defines the ISPIF private data model and public CAMSS entry points for older platforms that route CSID streams through ISPIF before VFE.

## Important APIs, Types, and Functions
Pad constants describe one sink and one source pad per ISPIF line. `enum ispif_intf` names PIX0, RDI0, PIX1, RDI1, and RDI2 interfaces. `struct ispif_intf_cmd_reg` caches command register values. `struct ispif_line` stores per-line media subdev state and selected routing endpoints. `struct ispif_device` stores global MMIO, IRQ, clocks, reset completions, power/config locks, interface commands, line array, and CAMSS pointer. Public functions are init/register/unregister.

## Control Flow
Common CAMSS probe calls `msm_ispif_subdev_init()`, then entity registration exposes one V4L2 subdev per ISPIF line. Link setup fills `csid_id`, `vfe_id`, and `interface`, which stream control later consumes.

## State and Persistence
All persistence is in RAM and hardware registers. The `power_count` is shared across lines, while format/routing state is per `ispif_line`.

## Dependencies and Integration Points
Depends on clock and V4L2/media headers plus `struct camss_subdev_resources`. Integrates with CSID and VFE media entities and CAMSS platform resource tables.

## Risks and Test Signals
The shared power counter and per-line routing fields are sensitive to link setup/teardown ordering. Compile tests should cover all users of the struct layout; runtime tests should validate multi-line stream concurrency, media graph links, and clean unregister with initialized mutexes.
