# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_escape.h

## Purpose

`svga_escape.h` defines VMware-specific SVGA escape command namespace values and the packed payload for fullscreen hint escape commands.

## Important APIs, Types, and Functions

- `SVGA_ESCAPE_NSID_VMWARE` and `SVGA_ESCAPE_NSID_DEVEL`: namespace identifiers for escape commands.
- `SVGA_ESCAPE_VMWARE_MAJOR_MASK`, `SVGA_ESCAPE_VMWARE_HINT`, and `SVGA_ESCAPE_VMWARE_HINT_FULLSCREEN`: VMware hint command IDs.
- `SVGAEscapeHintFullscreen`: packed payload with command ID, fullscreen flag, and monitor position `{ x, y }`.

## Control Flow

The header has no executable flow. Driver code emits an SVGA FIFO escape command with the VMware namespace, size, and this packed payload when it needs to send fullscreen hints to the host.

## State and Persistence Behavior

Fullscreen hint state is interpreted by the host. The header defines only the serialized message format and owns no persistent state.

## Dependencies and Integration Points

- Uses VMware fixed-width aliases from the broader include environment.
- Integrates with base FIFO `SVGA_CMD_ESCAPE` definitions in `svga_reg.h` and host UI/display hint handling.

## Risks and Edge Cases

- The struct is explicitly packed; any unpacked copy would change the host-visible wire layout.
- Namespace and command values must not collide with other escape families.
- Monitor coordinates are signed; callers should preserve negative positions for multi-monitor layouts.

## Test Signals

- Compile-time size checks for `SVGAEscapeHintFullscreen`.
- Escape construction tests should verify namespace, command, size, fullscreen flag, and signed coordinates.
