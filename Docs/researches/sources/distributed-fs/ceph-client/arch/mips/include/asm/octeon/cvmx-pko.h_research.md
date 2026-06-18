# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko.h

## Purpose
`cvmx-pko.h` is the hand-written Packet Output interface for Octeon. It defines PKO queue limits, locking modes, packet command/doorbell formats, status structures, initialization/configuration prototypes, inline send helpers, queue mapping helpers, counter reads, and rate-limit APIs.

## Important APIs, Types, And Functions
The file defines `CVMX_PKO_MAX_OUTPUT_QUEUES`, `CVMX_PKO_NUM_OUTPUT_PORTS`, illegal queue constants, and queue-depth constants. `cvmx_pko_status_t` reports success, invalid port/queue/priority, no memory, duplicate setup, and command queue init errors. `cvmx_pko_lock_t` selects no locking, POW atomic-tag locking, or command-queue ll/sc locking. `cvmx_pko_port_status_t` aggregates packets, octets, and doorbell count. `cvmx_pko_doorbell_address_t` builds the IO address used for packet-send doorbells, and `union cvmx_pko_command_word0` models the first PKO command word with checksum, gather, response, free, endian, FAU decrement, segment count, and byte length fields.

External APIs include `cvmx_pko_initialize_global()`, `cvmx_pko_enable()`, `cvmx_pko_disable()`, `cvmx_pko_shutdown()`, `cvmx_pko_config_port()`, `cvmx_pko_rate_limit_packets()`, and `cvmx_pko_rate_limit_bits()`. Inline APIs include `cvmx_pko_doorbell()`, `cvmx_pko_send_packet_prepare()`, `cvmx_pko_send_packet_finish()`, `cvmx_pko_send_packet_finish3()`, `cvmx_pko_get_base_queue_per_core()`, `cvmx_pko_get_base_queue()`, `cvmx_pko_get_num_queues()`, and `cvmx_pko_get_port_status()`.

## Control Flow
Send flow is split. `cvmx_pko_send_packet_prepare()` optionally switches to a POW atomic tag for exclusive queue access. `cvmx_pko_send_packet_finish()` waits for that tag switch if needed, writes a two-word command through `cvmx_cmd_queue_write2()`, rings the doorbell on success, and maps command-queue failures to PKO status codes. `finish3()` does the same for three-word commands and a completion/WQE address. `cvmx_pko_doorbell()` constructs an IO-segment doorbell address, issues `CVMX_SYNCWS`, and writes the command-word count. Counter reads select a port through `CVMX_PKO_REG_READ_IDX`, read count registers, optionally clear them, then read a model-specific debug register for doorbell state.

## State And Persistence
Persistent state lives in global PKO hardware and command-queue named blocks created by external initialization. Inline send helpers mutate POW tag state when atomic locking is selected and mutate command queues plus PKO doorbell state. Counter clear requests write back to PKO memory counters. The header itself stores no global state, although it declares `cvmx_pko_state_elem_t` as internal PKO state shape.

## Dependencies And Integration Points
The file includes FPA, POW, command queue, and PKO CSR definitions. It depends on `cvmx_write_io`, `cvmx_read_csr`, `cvmx_write_csr`, `CVMX_SYNCWS`, `cvmx_cmd_queue_write2/3`, `CVMX_CMD_QUEUE_PKO`, model macros, queue-per-port config macros, and buffer pointer definitions. It integrates with network drivers, packet buffers, POW scheduling, command queue allocation, and PKO global setup/teardown.

## Risks
Prepare and finish must be paired with identical port, queue, and locking arguments. Atomic-tag locking cannot be descheduled because it uses a fake WQE pointer. `CVMX_PKO_LOCK_NONE` relies entirely on caller serialization. Queue mapping depends on compile-time queue-per-port macros and model checks; unmapped ports return `CVMX_PKO_ILLEGAL_QUEUE`. Doorbell writes require prior command data visibility, hence the explicit sync. Counter clear semantics are indirect and can race with transmit activity. The little-endian bitfield branch defines `port:9` where comments describe 6 bits, so ABI assumptions should be checked against compiler layout and hardware expectations.

## Test Signals
Tests should cover status-code mapping for command queue success/full/no-memory/invalid results, doorbell address formation, memory barrier placement in send paths, atomic-tag prepare/finish ordering, command-queue locking mode, queue mapping for interface, PCI, loopback, CN68XX, and invalid ports, two-word versus three-word send commands, counter read and clear behavior, model-specific doorbell debug fields, and rate-limit API behavior on supported chips.
