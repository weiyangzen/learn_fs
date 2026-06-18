<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf04.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/srf04.c

Purpose: platform IIO driver for SRF04-style two-GPIO ultrasonic distance sensors and MaxBotix MB1000-series LV devices. It exposes one direct-mode `IIO_DISTANCE` channel with raw millimeter distance and scale, with optional power GPIO managed by runtime PM.

Important APIs, types, and functions: `struct srf04_data` stores trigger/echo/power GPIOs, mutex, IRQ, edge timestamps, completions, chip config, and startup delay. `srf04_read()` optionally resumes power, emits the trigger pulse, waits for echo rising/falling IRQ completions, converts pulse width to millimeters, and filters impossible long ranges. Runtime PM callbacks drive the optional power GPIO.

Control flow: probe gets trigger output and echo input GPIOs, optional power GPIO and `startup-time-ms`, rejects sleepable echo GPIOs, converts echo to IRQ, requests both-edge IRQ, registers a direct-mode IIO device, and enables runtime PM if power is present. Each read resumes power if needed, locks, sends the trigger pulse, schedules autosuspend, waits for echo edges, computes distance, and unlocks.

State and persistence: persistent state is GPIO handles, optional power startup delay, and timestamps/completions for the latest measurement. There is no hardware register state. The mutex prevents overlapping trigger/echo cycles.

Dependencies and integration points: depends on platform/OF matching, GPIO descriptors, IRQs, completions, runtime PM, and IIO direct mode. Compatibles include `devantech,srf04` and MaxBotix `mb1000` through `mb1040`.

Risks and test signals: test with and without power GPIO, startup-time override, echo IRQ timeouts, long-range rejection, IRQ polarity, and remove-time runtime PM cleanup. Risks include autosuspending shortly after trigger while echo is still being measured, no temperature compensation, and inability to work with sleepable GPIO controllers for echo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf04.c -->
