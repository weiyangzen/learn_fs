# sources/distributed-fs/openafs/src/rxkad/lifetimes.h

Purpose: Provides the Kerberos-style compact lifetime table used by rxkad ticket creation and decoding.

Important APIs/types: Defines `TKTLIFENUMFIXED`, `TKTLIFEMINFIXED`, `TKTLIFEMAXFIXED`, `TKTLIFENOEXPIRE`, `MAXTKTLIFETIME`, and the 64-entry `tkt_lifetimes` table mapping lifetime byte values `0x80` through `0xBF` to seconds.

Control flow and state: Header data only. `ticket.c` uses the table in `life_to_time` and `time_to_life`; values below `0x80` mean five-minute units, `0xFF` means no expiration, and the fixed range reaches 30 days.

Dependencies and integration: Included by `ticket.c`, `ticket5.c`, and `crc.c`. It ties ticket wire encoding to constants in `rxkad.p.h` such as `MAXKTCTICKETLIFETIME` and `NEVERDATE`.

Risks: The static table is protocol data; changing it changes ticket lifetime interpretation. The no-expire value remains a security-sensitive compatibility feature.

Test signals: Ticket tests and stress-generated tickets exercise `time_to_life`; server authentication paths exercise `life_to_time` and `tkt_CheckTimes`.
