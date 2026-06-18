# sources/distributed-fs/ceph-client/include/scsi/fc/fc_encaps.h

Purpose: Defines Fibre Channel frame encapsulation constants and SOF/EOF helpers based on RFC 3643.

Important APIs/types/functions: `struct fc_encaps_hdr` describes the FCIP-style encapsulation header with protocol/version complements, protocol data, length/flags, timestamp, CRC, and SOF. Enums define SOF, EOF, and FC classes. Helpers include `fc_sof_needs_ack()`, `fc_sof_normal()`, `fc_sof_class()`, and `fc_sof_is_init()`.

Control flow and state: This is a stateless wire-format header. Helpers derive class and ACK requirements from SOF byte encodings and convert initial SOF to normal SOF.

Dependencies and integration: Used by FCoE/libfc frame handling and FC frame allocation. Relies on FC payload size definitions from FC headers included elsewhere.

Risks and test signals: Risks include malformed macro definitions for redundant SOF/EOF encoding, incorrect frame length accounting, and class derivation errors. Tests should validate header size, SOF/EOF golden encodings, class helper results, and min/max encapsulated frame lengths.
