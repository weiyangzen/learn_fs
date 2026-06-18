<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.h -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.h

Purpose: defines the Exynos NoC Probe register offsets and bit masks used by `exynos-nocp.c`.

Important APIs and control flow: the header is macro/enum-only. `enum nocp_reg` maps control, statistic, alarm, source, alarm-mode, and value registers. Masks cover `NOCP_MAIN_CTL` enable bits, `NOCP_CFG_CTL` global/active bits, counter source event selection values such as cycle, busy, packet, byte, and chain, and counter alarm modes.

State and persistence behavior: none. It encodes the software-hardware ABI for the NoC Probe register block.

Dependencies and integration points: included only by the NoCP provider and relies on kernel `BIT()` availability through the including C file.

Risks and test signals: bitfield mistakes silently program wrong counters or alarms, causing governors to misread load. Test signals include register traces matching the Exynos hardware manual, `set_event()` programming byte/cycle sources as intended, and hardware counter values changing with synthetic memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-nocp.h -->
