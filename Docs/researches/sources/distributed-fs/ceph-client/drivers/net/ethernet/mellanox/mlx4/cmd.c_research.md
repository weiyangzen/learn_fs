# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/cmd.c

## Purpose
This is the mlx4 firmware command engine and SR-IOV command mediation layer. It posts commands through HCR registers or the VF communication channel, switches between polling and event completions, translates firmware statuses, manages command mailboxes, processes virtual HCR requests from slaves, initializes multi-function communication state, and exposes VF administration APIs.

## Important APIs and Functions
- `__mlx4_cmd()` is the central command dispatcher used by wrappers. It chooses native HCR polling/events or VF virtual-command path.
- `mlx4_cmd_poll()` and `mlx4_cmd_wait()` implement native polling and event completion over HCR.
- `mlx4_comm_cmd_poll()`, `mlx4_comm_cmd_wait()`, and `mlx4_slave_cmd()` implement slave-to-master communication channel commands.
- `mlx4_master_process_vhcr()` reads a slave vHCR/inbox, applies `cmd_info[]` policy, executes wrappers or native commands, writes outbox/status, and optionally generates a completion EQE.
- `mlx4_multi_func_init()` and `mlx4_multi_func_cleanup()` map communication pages and set up master/slave SR-IOV state.
- Exported VF APIs include `mlx4_set_vf_mac()`, `mlx4_set_vf_vlan()`, `mlx4_set_vf_rate()`, `mlx4_set_vf_spoofchk()`, `mlx4_get_vf_config()`, `mlx4_set_vf_link_state()`, and stats/SMI helpers.

## Control Flow
Native commands acquire command semaphores, wait for HCR readiness, write input/output parameters and opcode with memory ordering, then either poll the go bit or wait for a command event token. Multi-function slaves fill a shared vHCR and notify the PF; the PF workqueue decodes command-channel toggles, validates the expected boot/reset/VHCR sequence, processes commands through `cmd_info[]`, and writes status back. Error paths translate firmware status to errno and may enter internal error reset flow for fatal closing-command failures or timeouts.

## State and Persistence
State spans `priv->cmd` semaphores, HCR mapping, command context array, token mask/free list, mailbox DMA pool, polling/event mode, and communication toggles. Multi-function state spans mapped comm pages, per-slave state, admin and operational VF state, QoS managers, registered VLAN/MAC indexes, event EQ records, workqueues, and resource tracker state. VF admin settings persist in driver memory and often take effect on VF restart unless immediate update is possible.

## Dependencies and Integration Points
It integrates with firmware command opcodes, `fw.c` wrappers, resource tracker, RDMA subnet management packets, PCI MMIO, DMA pool mailboxes, devlink/internal reset handling, EQ command events, VLAN/MAC registration, QoS VPP firmware commands, network VF netlink APIs, and mlx4 Ethernet/RDMA resource consumers.

## Risks and Test Signals
Risks include command timeout recovery races, toggles becoming unsynchronized across FLR or misbehaving VMs, permission gaps in vHCR wrappers, mailbox DMA failures, inconsistent admin vs operational VF state, and fatal reset paths during close. Test signals include polling/event mode switching, SR-IOV VF boot handshake, VF command denial/allowance, FLR recovery, command timeout injection, VF VLAN/QoS/spoof/link configuration, and pending command wakeups on catastrophic error.
