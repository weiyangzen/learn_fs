<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.cc -->
# sources/distributed-fs/lizardfs/src/admin/options.cc

## Purpose
Implements the small long-option parser used by `lizardfs-admin` subcommands.

## Important APIs, Types, and Functions
Defines `Options::Options(expectedOptions, argv)` and `Options::parseOption(arg, expecting_value, valued_option)`. Expected option strings ending in `=` are treated as valued options with the visible option name trimmed.

## Control Flow, State, and Persistence
Construction initializes `options_` and `valued_options_`, then scans argv. If the previous valued option was waiting, the current argument becomes its value even if it starts with `--`. Otherwise `--`-prefixed arguments are parsed as options; all others become positional arguments. `--name=value` is accepted only for valued options, while bare valued options set `expecting_value` and mark the option as set. Missing values and unexpected options throw `Options::ParseError`. State persists in the `Options` object for a single command invocation.

## Dependencies and Integration Points
Depends on the `Options` header and C++ maps/vectors. `main.cc` builds the expected option list from each command's `supportedOptions`.

## Risks and Test Signals
Risks include no support for short options, no `--` end-of-options marker, valued options accepting the next positional argument silently, empty values accepted through `--opt=`, parse assertion on empty argv entries, and `std::stoi` conversion exceptions escaping as generic exceptions. Test signals are flags, valued options with separate and equals syntax, unexpected options, unexpected parameter on flag, missing value, values beginning with `--`, and positional arguments after options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.cc -->
