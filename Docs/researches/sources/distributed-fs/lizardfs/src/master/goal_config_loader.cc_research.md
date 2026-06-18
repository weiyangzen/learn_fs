# sources/distributed-fs/lizardfs/src/master/goal_config_loader.cc

Purpose: parses LizardFS goal configuration lines into `Goal` objects, supporting legacy standard-copy syntax and newer typed slice syntax for standard, XOR, and erasure-code goals.

Important APIs/types/functions: token helpers validate allowed characters and split on whitespace or `{ } $ : #`; `parseGoalId()` validates `GoalId` range; `parseGoalName()` validates name and colon; `parseSliceType()` handles `$std`, `$xor2..$xor9`, and `$ec(k,m)` plus optional braces; `parseLabels()` populates standard or per-part labels; `defaultGoal()` creates wildcard goals for unspecified ids; `parseLine()` parses one line; `load()` parses a stream, rejects duplicate ids, reports line-numbered parse errors, and fills defaults.

Control flow: `load()` reads line-by-line, skips empty/comment-only lines through tokenization, parses non-empty entries, stores them by id, checks stream errors, then adds default goals for every valid missing id.

State and persistence behavior: no persistent state. The returned map is process configuration used by goal management.

Dependencies/integration: depends on `Goal`, `GoalId`, `MediaLabelManager`, slice traits for erasure-code bounds/type conversion, and `ParseException`. Integrated by master goal configuration loading and tests.

Risks and test signals: the tokenizer rejects unexpected punctuation early, so config compatibility depends on allowed character maintenance. Standard goals check raw token count before label aggregation, while typed non-standard goals validate part count in `parseLabels()`. Tests should cover comments, whitespace/braces variants, duplicate ids, invalid names/labels, erasure bounds, default fill, stream I/O errors, and line-numbered errors.
