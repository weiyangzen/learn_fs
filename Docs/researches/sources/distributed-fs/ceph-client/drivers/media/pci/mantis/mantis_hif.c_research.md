# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.c

- Purpose: Implements the Mantis host interface for CAM memory and I/O space accesses through GPIF smart-buffer registers.
- Important APIs/types/functions: `mantis_hif_read_mem`, `mantis_hif_write_mem`, `mantis_hif_read_iom`, `mantis_hif_write_iom`, `mantis_hif_init`, `mantis_hif_exit`, and internal wait helpers.
- Control flow: Each access locks `ca_lock`, composes GPIF address bits for memory or I/O space, writes byte count/address/data registers, waits for smart-buffer opdone or write-ack, reads/writes data, and unlocks. Init configures slot slave timing and GPIF IRQ masks; exit clears BRRDY mask.
- State and persistence: Uses `slot[0].slave_cfg`, `hif_event`, `gpif_status`, and wait queues in `struct mantis_ca`; no persistent state.
- Dependencies and integration points: Integrated with `mantis_evm.c`, `mantis_pcmcia.c`, `mantis_link.h`, MMIO definitions, and EN50221 CAM access paths in the broader driver.
- Risks: Timeout checks compare `wait_event_timeout()` to `-ERESTARTSYS`, but that API returns 0 on timeout, so timeouts may be misreported. Fixed microsecond delays and single-slot assumptions make hardware timing fragile.
- Test signals: Exercise CAM attribute/common memory reads, I/O reads/writes, timeout injection, and concurrent EN50221 accesses while checking lock coverage and wakeups.
