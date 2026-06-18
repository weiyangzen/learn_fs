<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_monitor.py -->
# sources/distributed-fs/ceph-client/tools/workqueue/wq_monitor.py

## Purpose

`wq_monitor.py` is a Python/drgn utility script for inspecting live kernel state. It imports/defines WqStats, __init__, dict, table_header_str, table_row_str, sigint_handler, main and reads kernel symbols through drgn to print operational diagnostics.

## Important APIs, Types, and Functions

Source size: 168 lines, 6358 bytes. Functions/classes: WqStats, __init__, dict, table_header_str, table_row_str, sigint_handler, main. Python imports: signal, re, time, json, drgn, drgn.helpers.linux.list, argparse.

## Control Flow and Data Flow

Argument parsing builds filters and output mode, kernel objects are read from `prog`, helper functions format masks or stats, and the script either prints once or loops at the requested interval until interrupted.

## State and Persistence Behavior

The script stores only transient sampled values. Persistent state remains in the inspected kernel: workqueues, worker pools, backing-device writeback structures, or generated monitor inputs.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/workqueue`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

It depends on exact kernel symbol and struct names, BTF/debug info, and drgn helpers. Field layout changes or disabled configs can raise exceptions. JSON mode prints Python dict syntax in some scripts rather than strict serialized JSON.

## Test Signals

Run against a matching live kernel and vmcore, with and without filters, interval zero and repeated mode, and configs that disable optional NUMA/cgroup/writeback features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_monitor.py -->
