# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate_sequence_diagram.sh

Purpose: Bash helper that extracts protocol command names from `MFSCommunication.h` and prints sequence-diagram text showing sender-to-receiver message flow.

Important data/functions: maps protocol tokens `AN`, `CL`, `CS`, `MA`, `ML`, and `TS` to participant names. `print_header()` emits title and participants. `get_search_pattern()` builds a sender/receiver regex from active tokens. `get_transformation_pattern()` converts command names like `CLTOMA_*` into `CLIENT->MASTER:...`. `extract_sequence()` greps `#define` names, filters by token pattern, and applies sed transformations.

Control flow: accepts `path/to/MFSCommunication.h` followed by optional `PARTICIPANTS=...` and `ACTIONS=...` filters. It filters participant tokens before generating the regex and optionally filters emitted actions.

State and persistence: no files are written; output goes to stdout.

Dependencies/integration: depends on Bash associative arrays, `egrep`, `awk`, and `sed -E`. Output format is suitable for text sequence diagram tools.

Risks and test signals: argument parsing treats the source path as an `ARGUMENT` too but ignores unrecognized keys; values containing `=` are not handled. `set -e` is not enabled, and `grep` failures inside participant filtering can be surprising. Test signals are full protocol extraction, participant-limited diagrams, action filters, and LIZ-prefixed command handling.
