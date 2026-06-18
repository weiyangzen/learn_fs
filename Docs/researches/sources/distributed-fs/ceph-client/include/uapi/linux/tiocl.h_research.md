# sources/distributed-fs/ceph-client/include/uapi/linux/tiocl.h

## Purpose
Defines console `TIOCLINUX` subcommands and selection structures for virtual terminal selection, paste, blanking, mouse reporting, foreground console, scroll, and kernel message redirection controls.

## Important APIs, Types, and Constants
Selection commands include `TIOCL_SETSEL`, selection modes, `TIOCL_PASTESEL`, `TIOCL_UNBLANKSCREEN`, `TIOCL_SELLOADLUT`, `TIOCL_GETSHIFTSTATE`, `TIOCL_GETMOUSEREPORTING`, `TIOCL_SETVESABLANK`, `TIOCL_SETKMSGREDIRECT`, `TIOCL_GETFGCONSOLE`, `TIOCL_SCROLLCONSOLE`, `TIOCL_BLANKSCREEN`, `TIOCL_BLANKEDSCREEN`, `TIOCL_GETKMSGREDIRECT`, and `TIOCL_GETBRACKETEDPASTE`. `struct tiocl_selection` carries start/end coordinates and selection mode.

## Control Flow, State, and Persistence
Userspace passes a subcommand through tty ioctl mechanisms. Kernel virtual terminal state tracks selection contents, screen blanking, mouse reporting, foreground console, and message redirection.

## Dependencies and Integration Points
No explicit includes. Integrates with virtual terminal console code, gpm-like tools, console selection/paste, and tty ioctl paths.

## Risks and Test Signals
Risks include coordinate validation, selection visibility leaks, bracketed paste state, and console-only behavior on ptys. Test each subcommand on VTs, invalid coordinates, paste behavior, blank/unblank, and foreground console query.
