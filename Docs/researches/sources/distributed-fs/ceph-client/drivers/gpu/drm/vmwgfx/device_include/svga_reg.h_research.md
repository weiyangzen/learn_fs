# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_reg.h

## Purpose

`svga_reg.h` defines the base VMware SVGA II virtual hardware register, FIFO, command-buffer, screen, cursor, GMR, overlay, capability, and memory-size ABI. It is the non-3D foundation used by vmwgfx before and alongside SVGA3D command submission.

## Important APIs, Types, and Functions

- Device IDs and ports: `SVGA_ID_*`, index/value/BIOS/IRQ ports, IRQ flags, cursor limits, and register enum from `SVGA_REG_ID` through extended cursor/dirty/fence registers.
- Guest memory types: `SVGAMobId`, `SVGAGuestMemDescriptor`, `SVGAGuestPtr`, `SVGAGuestImage`, GMR constants, and image format descriptors.
- Command buffer ABI: maximum sizes, contexts, statuses, flags, packed `SVGACBHeader`, and device-context control commands.
- Capabilities: `SVGA_CAP_*`, `SVGA_CAP2_*`, backdoor capability types, FIFO register enum, FIFO caps/flags, and FIFO capability record structures.
- Overlay/video and screen state: overlay unit registers, `SVGAOverlayUnit`, display topology, screen flags, `SVGAScreenObject`, and screen DMA status values.
- FIFO 2D commands: `SVGAFifoCmdId` and packed payloads for update, rect copy, cursor definitions, fence, escape, screen define/destroy, GMRFB blits, annotations, GMR2 define/remap, and memory sizing constants.

## Control Flow

The header is declarative. Driver runtime flow uses register indices to probe device version/capabilities and configure memory/FIFO state, then writes FIFO commands with the packed payloads defined here. Command buffer fields let the driver submit larger command streams and observe completion/error/preemption status through volatile header fields.

## State and Persistence Behavior

The virtual device persists register values, FIFO positions/status, guest memory regions, command-buffer status, screen objects, overlay unit state, cursor state, and fences. This header defines the serialized and MMIO/register-visible forms of that state but does not implement accessors.

## Dependencies and Integration Points

- Includes `vm_basic_types.h`.
- Used across vmwgfx driver initialization, FIFO management, IRQ/fence handling, GMR/MOB memory code, KMS screen target code, overlay code, command-buffer submission, and SVGA3D headers.
- Escape command structures in `svga_escape.h` and `svga_overlay.h` build on `SVGA_CMD_ESCAPE` and video register constants from this file.

## Risks and Edge Cases

- Packed structures and enum numbers are host ABI and must remain stable.
- `volatile` command-buffer status fields require correct memory ordering in runtime code outside this header.
- FIFO and command size constants cap untrusted command data; validators must enforce them before writing to shared FIFO memory.
- 32-bit and 64-bit guest physical/page fields coexist. Callers must select the right descriptor form for capabilities and avoid truncation.
- Screen, overlay, and cursor dimensions need bounds checks against max constants to avoid host rejection or memory overrun.

## Test Signals

- Probe tests should validate version negotiation, register availability, capability bits, FIFO register layout, and IRQ mask/status behavior.
- Command construction tests should check packed sizes and payloads for base 2D commands, escapes, GMR2 remaps, and screen objects.
- Command-buffer tests should cover status transitions, queue-full/error/preempted handling, context flags, MOB vs physical-address submissions, and max-size enforcement.
