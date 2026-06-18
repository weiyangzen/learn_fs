<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_dump.py -->
# sources/distributed-fs/ceph-client/tools/workqueue/wq_dump.py

## Purpose

`wq_dump.py` is a Python/drgn utility script for inspecting live kernel state. It imports/defines err, cpumask_str, wq_type_str, print_pod_type and reads kernel symbols through drgn to print operational diagnostics.

## Important APIs, Types, and Functions

Source size: 249 lines, 8554 bytes. Functions/classes: err, cpumask_str, wq_type_str, print_pod_type. Python imports: sys, drgn, drgn.helpers.linux.list, drgn.helpers.linux.percpu, drgn.helpers.linux.cpumask, drgn.helpers.linux.nodemask, drgn.helpers.linux.idr, argparse.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_dump.py -->
