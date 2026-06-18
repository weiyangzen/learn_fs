# sources/distributed-fs/ceph-client/include/linux/libps2.h

Purpose: declares the shared PS/2 protocol helper layer for serio-attached keyboards, mice, and similar devices.

Important APIs and types: `enum ps2_disposition` lets a pre-receive handler process, ignore, or error a byte. Handler typedefs customize pre-receive and main receive behavior. `struct ps2dev` stores the serio port, command mutex, waitqueue, command flags, response buffer/count, NAK byte, and handlers. APIs initialize the struct, send bytes, drain input, bracket commands, execute commands including sliced commands, identify keyboard IDs, and handle serio interrupts.

Control flow: protocol drivers initialize `ps2dev`, use `ps2_command()` under serialized command handling, and feed interrupt bytes through `ps2_interrupt()`, which coordinates response collection and receive callbacks.

State and persistence: all state is volatile per device: command buffers, flags, waiters, and handler pointers. Hardware state changes are performed by PS/2 commands.

Dependencies and integration points: depends on serio, interrupts, mutexes, waitqueues, bitops, and input protocol drivers.

Risks and test signals: risks include command/interrupt races, timeout handling, NAK interpretation, buffer overflow, and callback lifetime during disconnect. Test command ACK/NAK paths, sliced commands, drain timeouts, keyboard ID detection, disconnect during command, and interrupt error flags.
