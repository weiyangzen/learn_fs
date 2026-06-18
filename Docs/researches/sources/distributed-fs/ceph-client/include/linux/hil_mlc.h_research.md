# sources/distributed-fs/ceph-client/include/linux/hil_mlc.h

## Purpose
`hil_mlc.h` defines the HP-HIL Master Link Controller abstraction and its state-engine nodes. It lets backend controller drivers implement low-level CTS/output/input operations while common MLC logic discovers devices, runs command sequences, and creates serio endpoints.

## Important APIs, Types, And Functions
Key definitions are `enum hilse_act`, `hilse_func`, `struct hilse_node`, backend callback typedefs `hil_mlc_cts`, `hil_mlc_out`, and `hil_mlc_in`, `struct hil_mlc_devinfo`, `struct hil_mlc_serio_map`, and `struct hil_mlc`. Public functions are `hil_mlc_register()` and `hil_mlc_unregister()`.

## Control Flow And State
The common MLC executes a state engine indexed by `seidx`. Nodes perform output, busy checks, input waits, expected-packet matching, last/discovery-device addressing, or callback functions. Semaphores signal loop idle, output dispatch, and input arrival. The controller tracks last operational device, discovery throttling, device info records, live device maps, serio devices, pending output packets, input packet buffers, timeouts, and a tasklet to drive progress.

## Dependencies And Integration Points
It depends on `hil.h`, time, interrupts, semaphores, serio, and lists. Backend drivers such as HP SDC MLC fill callback pointers and private data before registration. Serio children integrate discovered HIL devices with Linux input drivers.

## Risks
Risks include state-engine branch mistakes, timeout unit confusion (`suseconds_t` and usec args), semaphore imbalance, tasklet versus interrupt locking bugs, stale serio maps after reconfiguration, and overrun of fixed 16-entry device/info/input arrays. Discovery throttling fields must prevent endless loop reconfiguration storms.

## Test Signals
Test registration/unregistration, device discovery, lost-device reconfiguration, state-engine timeout/error branches, serio child creation/removal, concurrent interrupt input while output is pending, and backend failure injection for CTS/out/in callbacks.
