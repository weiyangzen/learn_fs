<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string.h -->
# sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string.h

## Purpose
Header-only helper to make single fields safe for simple space-separated porcelain output.

## Important APIs, Types, and Functions
Defines `std::string escapePorcelainString(std::string string)`. A local `replaceAll` lambda replaces backslashes with `\\` and double quotes with `\"`.

## Control Flow, State, and Persistence
The function first escapes backslashes, then quotes, tracks whether replacements occurred, and wraps the field in double quotes if it contains a space, is empty, or required escaping. It has no state.

## Dependencies and Integration Points
Used by `list_goals_command.cc` for goal definitions in porcelain mode. It depends only on `common/platform.h` and `std::string`.

## Risks and Test Signals
Risks include no escaping for tabs/newlines or other shell/CSV-sensitive bytes, header-defined non-`inline` function causing potential ODR/link issues if included by multiple translation units, and consumers assuming a full parser exists. Test signals are covered by `escape_porcelain_string_unittest.cc` for empty, spaces, quotes, and backslashes; additional signals should cover tabs/newlines if porcelain grammar expands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string.h -->
