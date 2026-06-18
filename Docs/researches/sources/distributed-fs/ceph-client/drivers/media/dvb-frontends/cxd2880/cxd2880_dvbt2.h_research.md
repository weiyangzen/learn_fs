# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt2.h

## Purpose
Defines DVB-T2 protocol enums and decoded signalling structures used by CXD2880 T2 tune and monitor paths.

## Important APIs, Types, and Functions
Enums cover profile, T2 version, S1/S2 signalling, guard, FFT mode, bandwidth code, L1 pre/post fields, PAPR, pilot pattern, PLP code rate/constellation/type/payload/FEC/mode, stream type, and PLP base/common selectors. Structures include `cxd2880_dvbt2_l1pre`, `cxd2880_dvbt2_plp`, `cxd2880_dvbt2_l1post`, `cxd2880_dvbt2_ofdm`, and `cxd2880_dvbt2_bbheader`.

## Control Flow
No direct flow. Monitor functions decode register blocks into these structures; tuning functions use profile and PLP fields to program selection.

## State and Persistence
Result structures are caller-owned snapshots of broadcast signalling. Profile and PLP selection can be persisted in tuner-demod active state through tune calls.

## Dependencies and Integration Points
Used heavily by `cxd2880_tnrdmd_dvbt2.c` and `cxd2880_tnrdmd_dvbt2_mon.c`, plus frontend glue converting monitor output into DVB core statistics.

## Risks and Edge Cases
Many reserved/unknown enum values must be handled explicitly. PLP arrays and counts need bounds checks against the DVB-T2 maximum and caller buffers. Mixed base/lite or MISO/SISO signalling affects diversity behavior and FEF settings.

## Test Signals
Streams covering base, lite, auto profile, multiple PLPs, common/data PLPs, rotated constellations, in-band signalling, and malformed/reserved L1 fields. Monitor output should match known transport metadata.
