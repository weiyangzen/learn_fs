<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.cpp

**Purpose:** Implements interactive terminal confirmation prompts for yes/no and exact typed confirmation flows.

**Important APIs/types/functions:** `uitk::userYNQuestion` and `uitk::userExactConfirmPrompt`.

**Control flow:** `userYNQuestion` repeatedly prints a prompt with default-sensitive casing, reads one line, uppercases and trims it, returns the default on empty input when provided, and accepts yes/no variants. Without a default, empty input clears `std::cin` and prompts again. `userExactConfirmPrompt` uppercases the required token and input, then loops until exact confirmation or `n`/`no`.

**State and persistence behavior:** No persistent state. It reads from an input stream but writes prompts to `std::cout` directly.

**Dependencies and integration points:** Uses Boost string algorithms and optional defaults. Useful for administrative commands that need destructive-action confirmation while permitting injectable input streams for tests.

**Risks:** Prompt output is always `std::cout`, even when input is a custom stream. Case-insensitive exact confirmation may be less strict than expected. Infinite loops are possible on EOF because stream state is not comprehensively handled.

**Test signals:** Tests should provide `std::istringstream` input for default, yes/no, exact match, abort, whitespace, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UiTk.cpp -->
