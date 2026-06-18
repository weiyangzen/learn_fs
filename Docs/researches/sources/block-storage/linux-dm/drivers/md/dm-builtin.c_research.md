# File Research: sources/block-storage/linux-dm/drivers/md/dm-builtin.c

Contains `dm_kobject_release()`, a tiny helper compiled into the kernel rather than the loadable DM module. The long file comment explains a module-unload race if the kobject release method lived in unloadable module text.

The race occurs when an external kobject reference delays release until after the DM device teardown waits on completion, the module unloads, and the delayed releaser resumes execution in freed module code. Keeping the release callback built-in avoids that executable-text lifetime problem.

The implementation simply calls `complete(dm_get_completion_from_kobject(kobj))` and exports the symbol for DM code.
