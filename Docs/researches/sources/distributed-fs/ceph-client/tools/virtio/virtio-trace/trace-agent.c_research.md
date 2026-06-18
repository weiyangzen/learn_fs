<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.c -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.c

## Purpose

`trace-agent.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 272 lines, 5417 bytes. Functions/classes: get_total_cpus, if, parse_size, if, usage, if, if, while, agent_main_loop, if, agent_info_free, main. Includes: limits.h, stdio.h, stdlib.h, unistd.h, trace-agent.h. Macros/defines: _GNU_SOURCE, PAGE_SIZE, PIPE_DEF_BUFS, PIPE_MIN_SIZE, PIPE_MAX_SIZE, TRACEFS, DEBUGFS, READ_PATH_FMT, WRITE_PATH_FMT, CTL_PATH.

## Control Flow and Data Flow

Local functions/macros include get_total_cpus, if, parse_size, if, usage, if, if, while, agent_main_loop, if, agent_info_free, main; includes are limits.h, stdio.h, stdlib.h, unistd.h, trace-agent.h. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/virtio-trace`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.c -->
