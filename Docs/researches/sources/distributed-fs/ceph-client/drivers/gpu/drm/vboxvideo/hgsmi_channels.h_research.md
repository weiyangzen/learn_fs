# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_channels.h

## Purpose

`hgsmi_channels.h` defines numeric HGSMI channel ids for VirtualBox guest-host graphics communication.

## Important APIs, Types, and Functions

- Fixed channels: reserved, HGSMI setup/configuration, VBVA graphics, seamless display modes, and OpenGL.
- String-mapped channel range: `HGSMI_CH_STRING_FIRST` through `HGSMI_CH_STRING_LAST`.

## Control Flow

HGSMI buffer allocation records a channel byte in `hgsmi_buffer_header`. The host routes the submitted buffer based on that channel and the channel-specific command id.

## State and Persistence Behavior

No runtime state. The constants are ABI-stable identifiers in shared buffers.

## Dependencies and Integration Points

Used by all HGSMI command helpers, VBVA ring flushing, modesetting protocol helpers, and cursor/capability submissions.

## Risks and Edge Cases

Values are protocol ABI and must not change. Commands sent on the wrong channel will be ignored or misinterpreted by the host.

## Test Signals

Compile-time inclusion plus runtime smoke tests for HGSMI setup and VBVA commands on a VirtualBox host validate channel routing.
