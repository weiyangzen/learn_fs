
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.c

## Purpose
ACPI platform driver for Huawei Kunpeng HCCS. It communicates with platform firmware over ACPI PCC mailboxes to discover chip/die/port topology, expose health/status counters through sysfs, and perform supported HCCS lane increase/decrease power-management operations.

## Important APIs, Types, and Functions
- PCC setup: `hccs_get_pcc_chan_id()`, `hccs_register_pcc_channel()`, `hccs_pcc_cmd_send()`, poll/IRQ wait helpers, and version-specific shared-memory fillers.
- Discovery: `hccs_get_dev_caps()`, chip/die/port query helpers, `hccs_get_hw_info()`, and `hccs_init_type_name_maps()`.
- Sysfs: kobject types for port/die/chip, show methods for type, lane mode, enable, current lane, FSM, lane mask, CRC counts, aggregate linked/full-lane status, and misc device attributes.
- PM lane control: `dec_lane_of_type_store()`, `inc_lane_of_type_store()`, idle/full-lane checks, and firmware commands for dec/inc/adapt/retraining.
- Probe/remove: `hccs_probe()` and `hccs_remove()`.

## Control Flow
Probe requires ACPI, obtains match-specific data for `HISI04B1` or `HISI04B2`, initializes a mutex, reads PCC channel id from `_CRS` generic register access size, registers the mailbox channel, verifies PCCT txdone mode and shared memory size, gets capabilities, discovers platform topology through firmware commands, builds type-name maps, and creates a sysfs topology tree under the device.

Every firmware command initializes a request descriptor, writes PCC header and command payload into shared memory, rings the mailbox doorbell, waits by polling or completion IRQ depending on ACPI ID, copies response back, and checks firmware `retStatus`. Sysfs show/store handlers take `hdev->lock` before issuing PCC commands. Lane decrease first verifies all matching ports are idle; lane increase skips work if all matching ports are already full lane and otherwise runs prepare/adapt/retraining sequence.

## State and Persistence
State lives in `struct hccs_dev`: capabilities, chip/die/port arrays, type-name maps, PCC channel, deadline, completion, and mutex. Topology is discovered at probe and exposed via kobjects until remove. Firmware counters and lane state are queried live through PCC. Lane changes persist in hardware/firmware state beyond a sysfs write.

## Dependencies and Integration Points
Depends on ACPI companion/match data, ACPI PCC mailbox, PCCT shared-memory layouts, sysfs/kobject APIs, mailbox completion semantics, and platform firmware implementing the HCCS command protocol described in `kunpeng_hccs.h`.

## Risks
- Firmware protocol, shared-memory size, and PCCT txdone mode must match ACPI ID; mismatches fail probe.
- Sysfs topology uses manual kobject lifetime; partial creation errors must unwind correctly.
- `used_types_show()` assumes `used_type_num > 0`; discovery currently rejects no-port/no-die cases before this, but future changes should preserve that invariant.
- Multi-BD/next-id logic rejects non-increasing `next_id`; malformed firmware can fail discovery.
- Lane decrease/increase sysfs writes can alter interconnect power/performance and rely on firmware idle/adaptation accuracy.

## Test Signals
ACPI-disabled probe rejection, missing `_CRS`, invalid PCC space id, PCCT txdone mismatch for both ACPI IDs, shared memory size mismatch, command timeout, firmware error retStatus, topology with multiple chips/dies/ports, sysfs read coverage, lane PM with unsupported type/busy ports/full-lane ports, and remove after partial sysfs creation.
