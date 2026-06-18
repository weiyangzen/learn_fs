# sources/cloud-native/moby/hack/validate/shfmt

## Purpose
Checks shell script formatting.

## Important APIs and Types
Uses `git grep --name-only '^#!'`, exclusion regexes, `xargs shfmt -d`, and flags `-bn -ci -sr`.

## Control Flow, State, and Persistence
The script finds shebang files excluding vendor, Go, Jenkinsfile, Python, and bats files. It runs `shfmt` in diff mode and prints success or a command to reformat.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on git, egrep, xargs, and shfmt. Risks include false positives from non-shell shebang files, missed shell files without shebangs, and xargs behavior with unusual paths. CI validation is the signal.
