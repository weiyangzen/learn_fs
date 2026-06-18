# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq_cmd.h

Purpose: this header defines iavf Admin Queue opcode values and the command/response payload layouts used by software and firmware.

Important APIs/types: `enum iavf_admin_queue_opc` lists AQ opcodes for versioning, queue shutdown, resource ownership, capabilities, switch/VSI management, MAC/VLAN/cloud filters, scheduler bandwidth, PHY/link, NVM, virtualization mailbox (`send_msg_to_pf/vf/peer`), alternate structure, LLDP, tunnels/RSS, async events, OEM, and debug commands. The file defines compile-time structure-length checks, `struct iavf_aqc_queue_shutdown`, `struct iavf_aqc_vsi_properties_data`, `struct iavf_aqc_get_veb_parameters_completion`, link-speed bits/enums, `struct iavf_aqc_pf_vf_message`, RSS key command/data structures, and RSS LUT command layout.

Control flow: command wrappers fill a `libie_aq_desc`, overlay the appropriate 16-byte direct command structure through `libie_aq_raw`, optionally attach indirect buffers using address fields, and send through `iavf_asq_send_command`. Static length assertions enforce firmware ABI size expectations.

State and persistence: no runtime state is stored here. The header defines on-wire/hardware ABI constants; changing them affects PF/FW communication and persisted hardware programming semantics such as VSI properties, VLAN modes, queue mapping, RSS key/LUT, and mailbox cookies.

Dependencies and integration: it includes `linux/net/intel/libie/adminq.h` for the base AQ descriptor and shared flags. It is consumed by `iavf_adminq.h`, `iavf_adminq.c`, and `iavf_common.c`.

Risks and test signals: ABI drift is the primary risk. Incorrect opcode values, field masks, endian annotations, or structure sizes can break firmware/PF compatibility. Test signals are compile-time struct-length assertions, AdminQ smoke tests for shutdown/RSS/mailbox, PF version compatibility, and runtime AQ error codes when commands are rejected.
