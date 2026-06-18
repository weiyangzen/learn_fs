# sources/distributed-fs/ceph-client/fs/smb/client/gen_smb2_mapping

Purpose: Perl build helper that generates an SMB2/SMB3 NT status to POSIX errno mapping table from annotated NT status header definitions, sorted by numeric status code.

Important APIs and functions: the script interface is `gen_smb2_mapping <in-h-file> <out-c-file>`. It uses `%statuses` to detect duplicate status macro names and `@list` to hold parsed records containing macro name, hex code string, numeric code, and errno text.

Control flow: argument validation requires two parameters. The input loop reads lines, matches defines of the form `#define STATUS_NAME cpu_to_le32(0x...) // -ERRNO`, skips severity helper macros, rejects duplicate status names, and stores parsed entries. After sorting by numeric code, it writes C initializer lines, skips zero status, and merges adjacent synonyms with the same numeric code into a single descriptive string joined with `or`. A padding calculation is retained but the final print emits a compact `{ code, error, "names" },` row.

State and persistence behavior: runtime state is temporary. The persistent artifact is the generated mapping table used by SMB2/SMB3 error handling to report Linux errors from protocol NTSTATUS responses. Like the SMB1 generator, the script treats structured comments as part of the source contract.

Dependencies and integration points: depends on Perl and a header that expresses statuses as `cpu_to_le32(hex)` with trailing POSIX errno comments. The generated output is consumed by SMB2 status/error mapping code in the CIFS client.

Risks: only one exact macro/comment style is recognized, so formatting changes in the input header can silently omit entries unless tests compare expected counts. Duplicate numeric values are intentionally merged, but duplicate macro names are fatal. Status code zero is skipped, so callers must handle success outside the generated error table. The script does not validate that errno names are real Linux errno constants.

Test signals: run generation against the current SMB2 status header; verify sorted numeric output and skipped zero status; introduce synonym status codes and confirm merged names; duplicate macro names should fail; malformed annotations should be detected by output count or build checks; and generated mappings should compile and translate representative SMB2/SMB3 errors.
