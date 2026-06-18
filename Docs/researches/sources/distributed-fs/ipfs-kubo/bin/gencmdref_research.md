# sources/distributed-fs/ipfs-kubo/bin/gencmdref

## Purpose
This Python utility generates a Markdown command reference by running `--help` for command lines supplied on stdin.

## Important APIs, Types, And Functions
`main` reads stdin lines, prints a top-level title/date/table of contents, then for each command runs `check_output((line + ' --help').split(' '))` and embeds the output in a fenced code block.

## Control Flow
With `-h` or `--help`, it prints usage. Otherwise it processes every input command in order.

## State And Persistence Behavior
It is a stdout generator only; callers redirect output to a Markdown file.

## Dependencies And Integration Points
It integrates with `ipfs commands` output and the local `ipfs` executable/command help system.

## Risks And Test Signals
Risks include Python 2 style print syntax, naive space splitting, and command help failures aborting generation. Signal is a complete Markdown command reference.
