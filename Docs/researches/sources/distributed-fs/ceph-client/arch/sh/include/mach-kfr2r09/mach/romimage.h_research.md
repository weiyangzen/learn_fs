<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/romimage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/romimage.h

Purpose: implements the KFR2R09 ROM-image progress hook in early assembly/C style.

Important APIs/types/functions: `mmcif_update_progress()` and inline label-based delay/control sequence.

Control flow: called repeatedly by MMCIF boot-copy code to show load progress on board hardware.

State and persistence: state is only the board display/GPIO latch touched by raw writes.

Dependencies/integration: integrates with KFR2R09 early boot before platform devices and LCD drivers are available.

Risks: timing-sensitive raw I/O and label flow can break if compiler assumptions change.

Test signals: test KFR2R09 ROM boot and confirm progress signaling does not disturb later device init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/romimage.h -->
