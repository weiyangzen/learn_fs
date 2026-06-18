<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.h

**Purpose:** Declares terminal UI confirmation helpers in namespace `uitk`.

**Important APIs/types/functions:** `userYNQuestion(question, defaultAnswer=boost::none, input=std::cin)` and `userExactConfirmPrompt(question, requiredInput, input=std::cin)`.

**Control flow:** The header exposes synchronous blocking calls. Input stream injection supports tests or scripted prompts, while output behavior is handled in the implementation.

**State and persistence behavior:** Stateless API; no persistence.

**Dependencies and integration points:** Includes Boost optional, iostream, and string. Used by CLI/admin flows requiring user confirmation.

**Risks:** Blocking prompts are inappropriate for daemon/non-interactive contexts. Callers should ensure stdin is interactive or provide a controlled input stream.

**Test signals:** Compile and unit tests can inject streams to avoid real terminal input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.h -->
