# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PrintableString.java

Purpose: converts a raw string to a printable form by replacing selected non-printable Unicode categories with `?`.

Important APIs and types: constructor `PrintableString(String)` and `toString()`. It scans Unicode code points and checks `Character.getType()`.

Control flow: for each code point it replaces control, format, private-use, surrogate, and unassigned categories with `REPLACEMENT_CHAR`; otherwise it appends the original code point.

State and persistence: immutable wrapper around the computed `printableString`; no external mutation.

Dependencies and integration: used by `Ls -q` to hide non-printable path characters while preserving printable Unicode.

Risks: category-based filtering may replace some invisible but meaningful characters and preserve others that terminals render oddly. Surrogate handling is based on code point iteration; malformed surrogate input is categorized as surrogate and replaced.

Test signals: cover ASCII pass-through, control characters, private-use, formatting marks, unassigned/surrogate cases, supplementary printable code points, and integration with `Ls`.
