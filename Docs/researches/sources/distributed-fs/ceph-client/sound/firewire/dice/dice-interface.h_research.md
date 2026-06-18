# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-interface.h

Purpose: documents and defines the DICE private FireWire register interface: section table, global registers, TX/RX stream registers, clock/status bits, and extended sync registers.

Important APIs/types: macro definitions for `DICE_PRIVATE_SPACE`, section offsets/sizes, `GLOBAL_OWNER`, `GLOBAL_NOTIFICATION`, clock select/status/capability fields, TX/RX register offsets, name sizes, AC3 fields, and extended sync fields.

Control flow and state: not executable code, but it defines how the driver reads section offsets, claims notification ownership, selects clock/rate, enables streams, programs ISO channels/speeds, and reads stream/channel/status data. State persists in device registers and is partly cleared by bus reset according to comments.

Dependencies/integration: consumed by DICE transaction, stream, proc, and detector files. Risks are register-version compatibility, all-quadlet byte-swapping of strings, write restrictions, and old firmware lacking later global fields. Test signals are successful subaddress validation, sane proc dumps, clock capability reads, and correct behavior after bus reset clears owner/enable.
