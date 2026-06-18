<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.h -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.h

Purpose: Defines the KB3310B EC public interface, IO ports, commands, register map, bit flags, and SCI event numbers.

Important APIs/types/functions: Declares EC access functions and `sci_handler`; exports `yeeloong_report_lid_status` hook. Constants cover fan, battery, audio, USB, lid, CRT, display, reset, LED, camera, WLAN, and SCI events.

Control flow: Header-only definitions are consumed by EC users to form command sequences and interpret event/register values.

State and persistence: No state; constants describe persistent EC firmware registers.

Dependencies and integration: Included by EC implementation, suspend wake logic, and reset logic.

Risks: Register addresses and bit meanings are firmware-specific. A wrong constant can power off devices, misreport battery status, or reset the machine.

Test signals: Drivers using the header should decode EC events like `EVENT_LID` and registers like `REG_LID_DETECT` consistently with real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.h -->
