# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/eq.c

## Purpose
`eq.c` implements mlx4 event queue management and interrupt dispatch. It creates and destroys EQs, maps events to EQs, handles legacy INTx and MSI-X interrupts, dispatches completions and asynchronous firmware events, forwards virtualized events to SR-IOV slaves, maintains slave port state transitions, handles FLR cleanup, exposes EQ vector allocation helpers, and provides interrupt self-tests.

## Important APIs, Types, and Functions
Public/exported APIs include `mlx4_gen_pkey_eqe()`, `mlx4_gen_guid_change_eqe()`, `mlx4_gen_port_state_change_eqe()`, `mlx4_get_slave_port_state()`, `set_and_calc_slave_port_state()`, `mlx4_gen_slaves_port_mgt_ev()`, `mlx4_master_handle_slave_flr()`, `mlx4_MAP_EQ_wrapper()`, `mlx4_alloc_eq_table()`, `mlx4_free_eq_table()`, `mlx4_init_eq_table()`, `mlx4_cleanup_eq_table()`, `mlx4_test_async()`, `mlx4_test_interrupt()`, `mlx4_is_eq_vector_valid()`, `mlx4_get_eqs_per_port()`, `mlx4_is_eq_shared()`, `mlx4_get_cpu_rmap()`, `mlx4_assign_eq()`, `mlx4_eq_get_irq()`, and `mlx4_release_eq()`.

Important internal helpers are `get_async_ev_mask()`, `eq_set_ci()`, `get_eqe()`, `next_eqe_sw()`, `next_slave_event_eqe()`, `mlx4_gen_slave_eqe()`, `slave_event()`, `mlx4_slave_event()`, `mlx4_set_eq_affinity_hint()`, `set_all_slave_state()`, `mlx4_eq_int()`, `mlx4_interrupt()`, `mlx4_msi_x_interrupt()`, `mlx4_MAP_EQ()`, `mlx4_SW2HW_EQ()`, `mlx4_HW2SW_EQ()`, `mlx4_num_eq_uar()`, `mlx4_get_eq_uar()`, `mlx4_create_eq()`, `mlx4_free_eq()`, and IRQ/clear-register mapping helpers. Core state lives in `struct mlx4_eq`, `struct mlx4_eq_table`, `struct mlx4_eqe`, slave event queues, EQ contexts, MTTs, IRQ names, CPU affinity masks, and SR-IOV slave state.

## Control Flow
Initialization allocates an EQ array and UAR map, initializes the EQ bitmap, maps the interrupt clear register for non-slaves, creates one async EQ plus completion EQs, allocates DMA-coherent EQ pages, writes MTTs, transitions EQ contexts from software to hardware, requests either a shared legacy IRQ or MSI-X IRQs, maps the async event mask, and arms the async EQ. Completion EQ IRQs can be requested lazily by `mlx4_assign_eq()` when a consumer asks for a vector.

`mlx4_eq_int()` is the central event loop. It reads EQEs whose owner bit indicates software ownership, issues a DMA read barrier, switches on the event type, and dispatches to CQ completion, QP/SRQ/CQ events, command completion, port change, EQ overflow, operation-required work, communication-channel work, FLR work, fatal warning, port management change, recoverable error, or warning logs. In master mode it maps QP/SRQ/CQ resources back to owning slaves and forwards events instead of dispatching locally when appropriate. The loop periodically writes the consumer index to avoid overflow and arms the EQ at the end.

SR-IOV event forwarding uses a software slave event queue protected by `event_lock`; `slave_event()` copies an EQE, stores a target slave or `ALL_SLAVES`, flips ownership, advances producer, and queues master communication work. `mlx4_gen_slave_eqe()` drains this queue and invokes `mlx4_GEN_EQE()` for target VFs, translating physical ports to slave ports for port-management events and suppressing bonded-port down notifications when another physical port is still up. FLR events mark slave state inactive/going down, dispatch a slave shutdown event, delete resources when the interface is up, reset slave state, and inform firmware that FLR is done.

## State and Persistence
There is no filesystem persistence. Persistent runtime state includes EQ DMA pages, MTTs, consumer indexes, IRQ registrations, UAR doorbell mappings, `actv_ports` bitmaps, vector refcounts, CPU rmap data, MSI-X pool bits, slave event producer/consumer indexes, slave port state, per-slave last command and activity flags, and interface workqueue items. Ordering is hardware-facing: owner-bit reads use `dma_rmb()`, generated slave EQEs use `dma_wmb()`, and EQ consumer doorbells use raw big-endian writes plus `wmb()`.

## Dependencies and Integration Points
This file ties firmware event delivery to mlx4 core subsystems: CQ/QP/SRQ event handlers, command event completion, resource tracking, SR-IOV communication, port sensing, workqueues, mlx4 event notifier dispatch, PCI IRQ/MSI-X allocation, CPU affinity/rmap, MTT allocation, and firmware commands `MAP_EQ`, `SW2HW_EQ`, and `HW2SW_EQ`. It is consumed by Ethernet, RDMA, and core code that need completion vectors or asynchronous device events.

## Risks
Risk centers on owner-bit parity and EQE stride calculations, CQ/EQ overflow if consumer indexes are not committed quickly enough, event forwarding to the wrong slave after port translation or resource lookup errors, bonded-port down suppression, FLR race handling during reset/load, IRQ teardown ordering with tasklets and `synchronize_irq()`, MSI-X vector refcount leaks, and capability-dependent async event masks. Incorrect port-state transitions can generate spurious IB up/down events or suppress required ones.

## Test Signals
Important tests are EQ creation/cleanup under MSI-X and shared IRQ, async NOP interrupt tests, completion interrupt tests per vector, port up/down events for Ethernet and IB, bonded mode event forwarding, CQ/QP/SRQ error events owned by PF and VF resources, command completions, communication channel events, FLR cleanup with active and inactive interfaces, recoverable cable events, IRQ affinity/rmap registration, vector assignment/release, and teardown with live interrupts.
