# sources/distributed-fs/coda/coda-src/scripts/volinfo.pl

Purpose: Perl formatter for Coda volume-list records, printing a simple volume overview with size, name, and id.

Control flow: defines a `stripleading` helper to remove the first character from tagged fields, sets Perl output formats, reads lines from stdin, splits fixed fields, strips leading marker characters from name/size/id, converts size from hex, stores size by name in `%volsize`, and writes formatted output.

State/persistence: read-only streaming transform; `%volsize` is process-local and not used after formatting in this script.

Dependencies, risks, tests: depends on old Coda `VolumeList` field layout and Perl formats. Risks include fixed-field parsing, no validation for short/malformed lines, and formatted columns that may truncate long values. Test with representative `volutil getvolumelist` output, malformed lines, hex size conversion, and long volume names.
