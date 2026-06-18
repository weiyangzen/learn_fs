## sources/distributed-fs/lizardfs/src/mount/polonaise/setup.h

Purpose: declares the Polonaise server configuration struct and global instance.

Important fields: master host/port, bind port or Windows pipe name, mountpoint, password, IO retry count, write buffer size, report-reserved period, forget-password flag, subfolder, debug flag, directory/entry/attribute cache settings, mkdir SGID behavior, `SugidClearMode`, daemonization, and deprecated ACL flag.

Integration: filled by command-line parsing and translated into `LizardClient::FsInitParams`.

Risks and tests: stores password as plaintext string until `main` copies it into params. Field defaults are not intrinsic to the struct; callers must run the parser or initialize every field.
