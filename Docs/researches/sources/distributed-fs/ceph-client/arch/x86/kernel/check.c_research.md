# sources/distributed-fs/ceph-client/arch/x86/kernel/check.c

## Purpose
This file reserves and periodically scans low physical memory to detect BIOS or firmware corruption.

## Important APIs, Types, and Functions
Boot parameters are parsed by `set_corruption_check()`, `set_corruption_check_period()`, and `set_corruption_check_size()`. `setup_bios_corruption_check()` reserves free low-memory scan areas and zeros them. `check_for_bios_corruption()` scans and clears nonzero words. `check_corruption()` reschedules delayed work, and `start_periodic_check_for_corruption()` starts the periodic scanner.

## Control Flow
Early setup decides whether the feature is enabled by boot parameter or config default. It rounds the scan size, walks free memblock ranges below the configured size, reserves up to eight aligned scan areas, zeros their direct mappings, and logs coverage. At device init, if areas exist and the period is nonzero, delayed work runs immediately and then every configured interval.

## State and Persistence
Persistent state includes `memory_corruption_check`, scan size and period, `scan_areas[]`, `num_scan_areas`, and the delayed work item. Reserved memblock regions remain unavailable for normal allocation so writes into them indicate corruption.

## Dependencies and Integration Points
The file depends on early boot params, memblock free range iteration and reservation, low-memory direct mapping via `__va`, workqueues, jiffies/HZ timing, and kernel warning/logging.

## Risks and Test Signals
Risks include reserving too much low memory, missing corruption outside the selected range, false positives from legitimate firmware reservations not excluded early enough, and repeated warning noise. Test signals include boot logs for reserved scan areas, periodic scan logs, injected low-memory writes causing a single warning, and disabled behavior with size zero or period zero.
