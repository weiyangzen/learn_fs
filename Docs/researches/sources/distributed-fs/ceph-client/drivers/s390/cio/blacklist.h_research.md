# sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.h

Purpose: tiny private CIO header exposing blacklist lookup to the rest of the common I/O subsystem.

Important APIs/types/functions: declares `is_blacklisted(int ssid, int devno)` and wraps it in include guards.

Control flow: no executable flow; consumers call the function during subchannel/device validation.

State and persistence: no state in the header; implementation state is the bitmap in `blacklist.c`.

Dependencies and integration: included by CIO files that need to check whether a device should be ignored.

Risks: the declaration uses plain `int` parameters and assumes callers pass values within bitmap bounds; bounds are enforced by parser/discovery paths rather than this header.

Test signals: compile coverage for CIO consumers and blacklist lookup behavior through `blacklist.c` tests.
