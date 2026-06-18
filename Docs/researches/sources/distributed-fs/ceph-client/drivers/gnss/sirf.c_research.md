# sources/distributed-fs/ceph-client/drivers/gnss/sirf.c

## Purpose
`sirf.c` is the SiRFstar serial GNSS driver. Unlike MTK and UBX, it implements its own serdev and power state machine to handle SiRF on/off pulse GPIOs, optional wakeup GPIO interrupts, regulators, and active/hibernate detection.

## Important APIs, Types, and Functions
`struct sirf_data` stores the GNSS device, serdev, speed, `vcc` and `lna` regulators, optional `on_off` and `wakeup` GPIOs, IRQ, active/open flags, serdev open count, mutexes, and wait queue. Important helpers are `sirf_serdev_open()`, `sirf_serdev_close()`, `sirf_open()`, `sirf_close()`, `sirf_receive_buf()`, `sirf_wait_for_power_state()`, `sirf_set_active()`, `sirf_runtime_suspend()`, and `sirf_runtime_resume()`.

## Control Flow
Probe allocates a GNSS device, initializes mutexes and wait queue, installs serdev callbacks, reads `current-speed` with default 9600 baud, gets mandatory regulators, and optionally gets `sirf,onoff` and `sirf,wakeup` GPIOs. With an on/off GPIO, it enables `vcc`, waits for boot into hibernate, samples or infers active state, requests a threaded wakeup IRQ if available, and forces hibernate if already active. Runtime PM is then enabled or, without PM, the device is powered active before GNSS registration.

Open marks the GNSS file open, opens serdev through a reference-counted helper, and runtime-resumes the device. Receive callbacks update active state when no wakeup GPIO is available and insert data only while the GNSS file is open. Suspend powers down by pulsing on/off or disabling `vcc`, then disables `lna`; resume reverses that sequence. Remove deregisters GNSS, disables PM or suspends, frees IRQ, disables always-on `vcc` for on/off boards, and drops the GNSS device.

## State and Persistence
State is volatile but richer than the generic serial helper: active state can be IRQ-driven or inferred from received data, serdev open is reference-counted separately from GNSS open, and power waits use a wait queue. No settings are persisted.

## Dependencies and Integration Points
The driver depends on GNSS core, serdev, regulator, GPIO descriptor, threaded IRQ, runtime PM, and OF compatibles for Fastrax, Linx, and Wi2Wi modules.

## Risks and Test Signals
When no wakeup GPIO exists, active/hibernate detection depends on receiving data within `SIRF_REPORT_CYCLE`, which comments call unreliable for long report intervals or motion-triggered output. Power failure rollback re-enables prior regulators and logs secondary failures. Tests should cover wakeup and no-wakeup boards, pulse retries, runtime and system suspend/resume, regulator failure rollback, open failure cleanup, receive while closed, and removal with the device open.
