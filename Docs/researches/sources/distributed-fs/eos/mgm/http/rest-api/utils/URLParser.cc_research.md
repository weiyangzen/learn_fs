## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.cc

Purpose: implements token-based URL prefix, pattern matching, parameter extraction, and duplicate-slash removal.

Important APIs/types/functions: constructor tokenizes on `/`; `startsBy`; `matches`; `matchesAndExtractParameters`; `removeDuplicateSlashes`. Parameter placeholders match regex `^\{[a-z]*\}$`.

Control flow: `startsBy` compares token prefixes. `matchesAndExtractParameters` requires equal token counts and treats placeholder tokens as captures. Captured map keys include the braces, e.g. `{requestid}`.

State and persistence: stores token vector for one parsed URL.

Dependencies and integration points: used by `RestHandler`, `RestApiManager`, `Router`, actions, and `FilesContainer`.

Risks and test signals: token counts are stored in `uint8_t`, so very long URLs can truncate sizes. Placeholder regex accepts empty `{}` and only lowercase letters. Tests should cover trailing slashes, duplicate slashes, encoded slashes, and parameter key expectations.
