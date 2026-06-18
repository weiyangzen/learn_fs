# sources/distributed-fs/ceph-client/tools/perf/util/pfm.h

## Purpose
This header provides the conditional public interface for libpfm4 integration. It lets callers use libpfm parsing and listing when available while compiling to no-op stubs without libpfm.

## Important APIs, Types, and Functions
With `HAVE_LIBPFM`, it declares `parse_libpfm_events_option` and `print_libpfm_events`. Without it, inline stubs return success for parsing and emit nothing for listing.

## Control Flow
The header uses preprocessor selection to either declare real functions or define inline no-op replacements. There is no runtime branching here.

## State and Persistence
No state is owned by the header. The real implementation mutates evlists, while stubs intentionally do not.

## Dependencies and Integration Points
It depends on `print-events.h` and subcmd parse-options. It is included by command-line parsing and event-listing code that should not care whether libpfm was built in.

## Risks
The disabled stub for parsing returns zero, so callers must ensure the option is not exposed or is documented correctly when libpfm support is absent. Otherwise a user-provided libpfm option could appear accepted but produce no events.

## Test Signals
Build tests should cover both `HAVE_LIBPFM` and non-libpfm configurations. CLI tests should ensure unavailable libpfm options are either hidden or handled explicitly by higher layers.
