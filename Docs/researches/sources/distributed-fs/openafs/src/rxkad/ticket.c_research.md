# sources/distributed-fs/openafs/src/rxkad/ticket.c

Purpose: Implements legacy Kerberos v4/Athena-style rxkad ticket assembly, encryption, decryption, lifetime conversion, and time validation.

Important APIs/functions: `tkt_DecodeTicket` DES-PCBC decrypts a ticket and parses client/server fields. `tkt_MakeTicket` assembles and DES-PCBC encrypts a ticket. `tkt_CheckTimes` validates start/end/now with skew and max lifetime. `ktohl` handles ticket-endian flags. `life_to_time` and `time_to_life` convert compact lifetime bytes.

Control flow and state: Decode validates ticket length and 8-byte alignment, schedules DES key, decrypts using the key as IV, parses strings and session key, computes end time, and checks time validity. Encode validates strings, writes fields in network order, computes a lifetime byte, rounds to 8 bytes, and encrypts in place.

Dependencies and integration: Uses hcrypto DES, Rx error codes, `lifetimes.h`, `rxkad.h`, and key conversion helpers. Server response validation calls it for non-v5 tickets; stress client uses it to generate test tickets.

Risks: DES PCBC and v4 ticket formats are legacy. String parsing uses bounded protocol maxima but relies on decrypted NUL-terminated fields. `NEVERDATE` tickets are accepted subject to server policy.

Test signals: Stress-generated tickets exercise encode/decode; server auth paths exercise decode and time validation.
