<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NamedException.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/NamedException.h

Purpose: Defines BeeGFS named exception infrastructure and a macro for derived exception classes.

Important APIs/types: `DECLARE_NAMEDEXCEPTION` and `DECLARE_NAMEDSUBEXCEPTION` generate exception classes with constructors that pass an exception name and message to the base. `NamedException` derives from `std::exception`, stores the name/message internally, and exposes `what()` for the message text.

Control flow/state/persistence: Exception messages are stored in `std::string`; `what()` returns a stable C string from a member buffer/string. No persistence.

Dependencies/integration: Base for synchronization, config, signal, and other BeeGFS exception families.

Risks/test signals: `what()` lifetime and message preservation are critical for logging. Tests should cover message constructors, catch by `std::exception`, copy behavior, and macro-generated inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NamedException.h -->
