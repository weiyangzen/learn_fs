<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-callback.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-method-callback.h

Purpose: Declares callback hooks that transport methods use to notify the generic BMI layer about method-discovered address lifecycle events.

Important APIs, types, and functions: `bmi_method_addr_reg_callback(bmi_method_addr_p map)` registers a method address discovered by an unexpected receive and returns a generic `BMI_addr_t`. `bmi_method_addr_forget_callback(BMI_addr_t addr)` asks BMI to consider dropping an inactive address later. `bmi_method_addr_drop_callback(char *method_name)` requests forced cleanup for inactive addresses owned by a method.

Control flow and state: This header has no state. The implementations in `bmi.c` enqueue forget/drop work or create reference-list entries, so method code can avoid direct access to BMI's internal reference list.

Dependencies and integration points: Includes `bmi-method-support.h` for `bmi_method_addr_p` and `pvfs2-internal.h`. Used by methods such as GM when a peer sends an unexpected message from an address not yet known to BMI.

Risks and test signals: Callers must only register truly new method addresses; the generic callback trusts methods and does not deduplicate. Tests should verify unexpected peer discovery, address reuse, forget-list draining, and forced drop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-callback.h -->
