<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.h

Purpose: Declares the Cobalt CPLD status and frequency programming APIs.

Important APIs/types: `cobalt_cpld_status(struct cobalt *cobalt)` logs board/CPLD telemetry. `cobalt_cpld_set_freq(struct cobalt *cobalt, unsigned freq)` programs the HSMA output oscillator and returns success/failure.

Control flow: Consumers call status from diagnostic paths and frequency setup from video output start.

State/persistence: No header state. Functions operate on hardware state behind `struct cobalt`.

Dependencies/integration: Includes `cobalt-driver.h` for the `struct cobalt` definition and bus helpers.

Risks: The header exposes hardware-side effects through a simple boolean API; callers cannot distinguish unsupported frequency from oscillator readback retry failure.

Test signals: Compile/link checks and output streaming paths that call `cobalt_cpld_set_freq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.h -->
